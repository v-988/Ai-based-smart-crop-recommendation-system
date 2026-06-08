"""
LLM Service
Handles AI chatbot functionality using OpenRouter API.
Includes chat memory, smart continuation, and multilingual support.
"""

import httpx
import asyncio
import re
from typing import Optional, AsyncGenerator, List, Dict
from loguru import logger

try:
    from deep_translator import GoogleTranslator
except Exception:  # pragma: no cover - optional runtime dependency
    GoogleTranslator = None

from config.settings import settings
from models.schemas import LanguageEnum, ChatMessage
from utils.helpers import clean_markdown_text, is_sentence_complete, sanitize_input


class ChatMemory:
    """
    In-memory chat history manager.
    Maintains conversation context for better responses.
    """
    
    def __init__(self, max_messages: int = 10):
        """
        Initialize chat memory.
        
        Args:
            max_messages: Maximum number of messages to retain
        """
        self.max_messages = max_messages
        self.sessions: Dict[str, List[ChatMessage]] = {}
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to session history."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append(
            ChatMessage(role=role, content=content)
        )
        
        # Trim old messages
        if len(self.sessions[session_id]) > self.max_messages:
            self.sessions[session_id] = self.sessions[session_id][-self.max_messages:]
    
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get formatted history for API call."""
        if session_id not in self.sessions:
            return []
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.sessions[session_id]
        ]
    
    def get_context_string(self, session_id: str) -> str:
        """Get history as formatted string."""
        history = self.get_history(session_id)
        return "\n".join(
            f"{'Farmer' if m['role'] == 'user' else 'AI'}: {m['content']}"
            for m in history
        )
    
    def clear_session(self, session_id: str):
        """Clear a specific session's history."""
        if session_id in self.sessions:
            del self.sessions[session_id]


class LLMService:
    """
    Service for AI-powered agricultural chatbot using OpenRouter.
    Supports Tamil and English languages with smart response completion.
    """
    
    def __init__(self):
        """Initialize the LLM service with configuration."""
        self.openrouter_api_key = settings.OPENROUTER_API_KEY
        self.openrouter_model = settings.OPENROUTER_MODEL
        self.openrouter_fallback_models = [
            m.strip() for m in getattr(settings, "OPENROUTER_FALLBACK_MODELS", "").split(",") if m.strip()
        ]
        self.openrouter_base_url = settings.OPENROUTER_BASE_URL

        self.groq_api_key = settings.GROQ_API_KEY
        self.groq_model = settings.GROQ_MODEL
        self.groq_fallback_models = [
            m.strip() for m in getattr(settings, "GROQ_FALLBACK_MODELS", "").split(",") if m.strip()
        ]
        self.groq_base_url = settings.GROQ_BASE_URL

        self.max_tokens = max(settings.MAX_TOKENS, 900)
        self.temperature = settings.TEMPERATURE
        self.max_continuation_loops = max(settings.MAX_CONTINUATION_LOOPS, 3)

        self.openrouter_enabled = self._is_real_api_key(
            self.openrouter_api_key,
            "your_openrouter_api_key_here"
        )
        self.groq_enabled = self._is_real_api_key(
            self.groq_api_key,
            "your_groq_api_key_here"
        )

        self.demo_mode = not (self.openrouter_enabled or self.groq_enabled)

        if self.demo_mode:
            logger.warning("No LLM provider API key configured - running in demo mode")
        elif not self.openrouter_enabled:
            logger.warning("OpenRouter not configured - using Groq as primary provider")
        elif not self.groq_enabled:
            logger.info("Groq not configured - using OpenRouter only")

        self.openrouter_headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://plant-disease-chatbot.com",
            "X-Title": "Plant Disease Detection Chatbot"
        }

        self.groq_headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        self.openrouter_model_candidates = self._build_model_candidates(
            self.openrouter_model,
            self.openrouter_fallback_models,
            default_fallback_chain=[
                "arcee-ai/trinity-mini:free",
                "nvidia/nemotron-3-super-120b-a12b:free",
                "stepfun/step-3.5-flash:free",
            ]
        )
        self.groq_model_candidates = self._build_model_candidates(
            self.groq_model,
            self.groq_fallback_models,
            default_fallback_chain=[
                "llama-3.1-8b-instant",
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
            ]
        )
        
        # Chat memory instance
        self.memory = ChatMemory(max_messages=settings.MAX_CHAT_HISTORY)

    def _is_real_api_key(self, key: str, placeholder: str) -> bool:
        """Check whether an API key is configured with a non-placeholder value."""
        return bool(key and key != placeholder and len(key) >= 12)

    def _translate_text(self, text: str, source: str, target: str) -> str:
        """Translate text with safe fallback to the original content."""
        if not text.strip():
            return text
        if source == target:
            return text
        if GoogleTranslator is None:
            return text

        try:
            translated = GoogleTranslator(source=source, target=target).translate(text)
            return translated.strip() if translated else text
        except Exception as e:
            logger.warning(f"Translation failed ({source}->{target}): {e}")
            return text

    def _translate_long_text(self, text: str, source: str, target: str) -> str:
        """Translate long text in chunks to avoid provider length issues."""
        if not text.strip():
            return text

        # Chunk by paragraph while preserving line breaks.
        parts = text.split("\n")
        translated_parts = [self._translate_text(part, source, target) if part.strip() else "" for part in parts]
        return "\n".join(translated_parts)

    def _contains_tamil(self, text: str) -> bool:
        """Check whether text contains Tamil script characters."""
        return bool(re.search(r"[\u0B80-\u0BFF]", text or ""))

    def _build_model_question(self, message: str, detected_language: LanguageEnum) -> str:
        """Build a model-friendly question while preserving the original text."""
        if detected_language == LanguageEnum.TAMIL or self._contains_tamil(message):
            translated = self._translate_text(message, source="ta", target="en")
            if translated.strip() and translated.strip().lower() != message.strip().lower():
                return (
                    "Original Tamil question:\n"
                    f"{message}\n\n"
                    "English translation (use this for reasoning):\n"
                    f"{translated}"
                )

        return message

    def _get_provider_fallback_response(
        self,
        message: str,
        disease_context: Optional[str],
        language: LanguageEnum
    ) -> str:
        """Return a useful local fallback when provider/models are unavailable."""
        base_response = self._get_demo_response(message, disease_context, language)

        if language == LanguageEnum.TAMIL:
            return (
                "இப்போது AI சேவை தற்காலிகமாக கிடைக்கவில்லை. "
                "ஆனால் உங்கள் கேள்விக்கான பயனுள்ள வழிகாட்டியை கீழே கொடுக்கிறேன்.\n\n"
                f"{base_response}"
            )

        return (
            "AI service is temporarily unavailable right now. "
            "I am sharing a useful fallback answer below.\n\n"
            f"{base_response}"
        )

    def _build_model_candidates(
        self,
        primary_model: str,
        fallback_models: List[str],
        default_fallback_chain: List[str]
    ) -> List[str]:
        """Build ordered, unique model fallback list for a provider."""
        candidates = []
        if primary_model:
            candidates.append(primary_model.strip())
        if fallback_models:
            candidates.extend(fallback_models)
        else:
            candidates.extend(default_fallback_chain)

        unique_candidates = []
        seen = set()
        for model in candidates:
            if model and model not in seen:
                unique_candidates.append(model)
                seen.add(model)

        return unique_candidates
    
    def _get_demo_response(self, message: str, disease_context: Optional[str] = None, language: LanguageEnum = LanguageEnum.ENGLISH) -> str:
        """Generate demo response when API key is not configured."""
        if language == LanguageEnum.TAMIL:
            if disease_context:
                return f"""நோய் கண்டறியப்பட்டது: {disease_context}

சிகிச்சை பரிந்துரைகள்:
1. பாதிக்கப்பட்ட இலைகளை உடனடியாக அகற்றவும்
2. தாமிர அடிப்படையிலான பூஞ்சைக் கொல்லியைப் பயன்படுத்தவும்
3. காற்றோட்டத்தை மேம்படுத்த செடிகளுக்கிடையே இடைவெளி விடவும்
4. தினசரி செடிகளை கண்காணிக்கவும்

குறிப்பு: இது டெமோ பதில். முழு AI திறன்களுக்கு OpenRouter API விசையை கட்டமைக்கவும்."""
            return f"""வணக்கம்! நான் உங்கள் விவசாய உதவியாளர்.

நீங்கள் கேட்டது: {message[:100]}...

டெமோ பயன்முறையில் இயங்குகிறது. AI சாட்போட்டை முழுமையாகப் பயன்படுத்த:
1. OpenRouter.ai இல் கணக்கை உருவாக்கவும்
2. API விசையைப் பெறவும்
3. Backend .env கோப்பில் OPENROUTER_API_KEY ஐ புதுப்பிக்கவும்

உங்கள் விவசாய கேள்விகளுக்கு உதவ தயாராக இருக்கிறேன்!"""
        else:
            if disease_context:
                return f"""Disease Detected: {disease_context}

Treatment Recommendations:
1. Remove and destroy infected leaves immediately
2. Apply copper-based fungicide (follow package instructions)
3. Improve air circulation by spacing plants properly
4. Water at the base of plants, avoiding wet leaves
5. Monitor plants daily for new symptoms

Prevention Tips:
- Rotate crops each season
- Use disease-resistant varieties
- Maintain proper plant nutrition

Note: This is a demo response. Configure OPENROUTER_API_KEY for full AI capabilities."""
            
            return f"""Hello! I'm your agricultural assistant.

You asked: {message[:100]}...

I'm currently running in demo mode. To enable full AI chatbot capabilities:
1. Get an API key from OpenRouter.ai
2. Update OPENROUTER_API_KEY in backend/.env file
3. Restart the backend server

Common topics I can help with:
- Plant disease identification and treatment
- Crop management best practices
- Pest control solutions
- Soil health and fertilization
- Irrigation guidance

Once configured, I'll provide personalized advice for your farming questions!"""
    
    def _get_system_prompt(self, language: LanguageEnum) -> str:
        """
        Generate system prompt based on language preference.
        
        Args:
            language: Preferred response language
            
        Returns:
            System prompt string
        """
        lang_name = language.value if language else "English"
        
        if language == LanguageEnum.TAMIL:
            return """நீங்கள் ஒரு விவசாய நிபுணர். விவசாயிகளின் கேள்விக்கு கேள்வி-சார்ந்த முறையில் பதிலளிக்கவும்.

முக்கிய விதிகள்:
1. தமிழில் மட்டுமே பதிலளிக்கவும்.
2. கேள்வியின் நோக்கத்தை முதலில் புரிந்து அதற்கே பொருத்தமாக பதிலளிக்கவும்.
3. ஒவ்வொரு பதிலும் ஒரே template ஆக இருக்கக்கூடாது.
4. பயனர் steps கேட்டால் மட்டும் எண் பட்டியல் பயன்படுத்தவும்; இல்லையெனில் இயல்பான உரையாடல் வடிவம் பயன்படுத்தவும்.
5. "ஏன்" அல்லது "காரணம்" கேள்வி வந்தால் முதலில் 2-4 வாக்கியங்களில் நேரடி காரண விளக்கம் அளிக்கவும்; எண் பட்டியல் கட்டாயமில்லை.
6. தேவையான அளவு மட்டுமே எழுதவும்: சின்ன கேள்விக்கு சின்ன பதில், சிக்கலான கேள்விக்கு விரிவான பதில்.
7. பயனர் கொடுத்த பயிர்/அறிகுறி/நிலைமையை குறிப்பாக address செய்யவும்.
8. **, #, ``` போன்ற markdown குறியீடுகளை பயன்படுத்த வேண்டாம்.
9. தெளிவான, நடைமுறை, பாதுகாப்பான ஆலோசனை வழங்கவும்.
10. தேவையான போது 1 அல்லது 2 தெளிவான தொடர்க் கேள்வி கேட்கவும்.
11. நட்பு, ஆதரவு, நம்பிக்கையூட்டும் தொனி வைத்திருக்கவும்.

தவிர்க்கவேண்டியது:
- எல்லா பதில்களிலும் ஒரே Cure & Prevention template பயன்படுத்துதல்
- பயனர் கேள்வியுடன் தொடர்பில்லாத பொதுவான நீளமான பட்டியல்

உங்கள் நிபுணத்துவம்:
- தாவர நோய் அடையாளம் மற்றும் சிகிச்சை
- பயிர் மேலாண்மை
- மண் ஆரோக்கியம்
- பூச்சி கட்டுப்பாடு
- நீர்ப்பாசன மேலாண்மை
- இந்திய விவசாய நடைமுறைகள்"""
        
        return f"""You are an expert agricultural advisor helping farmers with plant diseases and farming questions.

    IMPORTANT RULES:
    1. Reply ONLY in {lang_name} language.
    2. Understand the user's exact intent and answer that specific question first.
    3. Do not use the same template for every response.
    4. Use numbered steps only when the user asks for steps, a plan, or treatment protocol; otherwise respond in natural conversational prose.
    5. For "why" or "cause" questions, start with a direct explanation in 2-4 sentences before any optional tips.
    6. Keep response length proportional to question complexity.
    7. Reference the user's crop, symptom, and context directly instead of generic advice.
    8. Do NOT use markdown symbols like **, #, or ```.
    9. Be practical, safe, and actionable.
    10. Prefer organic/sustainable approaches when suitable, but do not force a fixed sectioned format.
    11. Ask up to 2 clarifying questions only when needed due to missing critical details.

    AVOID:
    - Repeating a fixed "Cure & Prevention" structure for unrelated questions
    - Long generic lists when a short direct answer is enough

    You have expertise in:
    - Plant disease identification and treatment
    - Crop management and best practices
    - Soil health and fertilization
    - Pest control (organic and chemical)
    - Irrigation and water management
    - Seasonal farming advice
    - Local farming practices in India"""
    
    async def chat(
        self,
        message: str,
        session_id: str,
        disease_context: Optional[str] = None,
        language: Optional[LanguageEnum] = None
    ) -> str:
        """
        Process a chat message and return AI response.
        
        Args:
            message: User's message
            session_id: Session ID for context
            disease_context: Detected disease name for context
            language: Preferred response language
            
        Returns:
            AI response string
        """
        try:
            # Sanitize input
            message = sanitize_input(message)
            
            # Detect language if not specified
            detected_language = self._detect_language(message)
            response_language = language or detected_language
            model_language = LanguageEnum.ENGLISH if response_language == LanguageEnum.TAMIL else response_language
            
            # Return demo response if API key not configured
            if self.demo_mode:
                response = self._get_demo_response(message, disease_context, response_language)
                self.memory.add_message(session_id, "user", message)
                self.memory.add_message(session_id, "assistant", response)
                return response
            
            # Build context
            context_parts = []
            
            if disease_context:
                normalized_context = disease_context
                if self._contains_tamil(disease_context):
                    translated_context = self._translate_text(disease_context, source="ta", target="en")
                    if translated_context and translated_context != disease_context:
                        normalized_context = f"{disease_context} (English: {translated_context})"
                context_parts.append(f"Disease detected: {normalized_context}")
            
            # Get chat history
            history_context = self.memory.get_context_string(session_id)
            if history_context:
                context_parts.append(f"Previous conversation:\n{history_context}")
            
            model_question = self._build_model_question(message, detected_language)
            context_parts.append(f"Farmer's question: {model_question}")
            full_prompt = "\n\n".join(context_parts)
            
            # Get response with smart continuation
            response = await self._get_complete_response(
                full_prompt,
                model_language
            )

            if not response or not response.strip():
                retry_prompt = full_prompt + "\n\nProvide one clear final answer now."
                response = await self._get_complete_response(retry_prompt, model_language)

            if not response or not response.strip():
                if response_language == LanguageEnum.TAMIL:
                    response = "மன்னிக்கவும், இப்போது தெளிவான பதிலை உருவாக்க முடியவில்லை. தயவு செய்து கேள்வியை சற்று மாற்றி மீண்டும் அனுப்புங்கள்."
                else:
                    response = "Sorry, I could not generate a clear answer right now. Please rephrase your question and try again."

            if response_language == LanguageEnum.TAMIL:
                translated_response = self._translate_long_text(response, source="en", target="ta")
                if translated_response.strip():
                    response = translated_response
            
            # Store in memory
            self.memory.add_message(session_id, "user", message)
            self.memory.add_message(session_id, "assistant", response)
            
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            active_lang = language or self._detect_language(message)
            return self._get_provider_fallback_response(
                message=message,
                disease_context=disease_context,
                language=active_lang
            )
    
    async def chat_stream(
        self,
        message: str,
        session_id: str,
        disease_context: Optional[str] = None,
        language: Optional[LanguageEnum] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response for real-time display.
        
        Args:
            message: User's message
            session_id: Session ID
            disease_context: Disease context
            language: Preferred language
            
        Yields:
            Response chunks as they arrive
        """
        try:
            message = sanitize_input(message)
            
            detected_language = self._detect_language(message)
            response_language = language or detected_language
            model_language = LanguageEnum.ENGLISH if response_language == LanguageEnum.TAMIL else response_language
            
            # Return demo response if API key not configured
            if self.demo_mode:
                demo_response = self._get_demo_response(message, disease_context, response_language)
                # Simulate streaming by yielding words
                words = demo_response.split()
                for i, word in enumerate(words):
                    yield word + (" " if i < len(words) - 1 else "")
                    await asyncio.sleep(0.03)  # Small delay for streaming effect
                self.memory.add_message(session_id, "user", message)
                self.memory.add_message(session_id, "assistant", demo_response)
                return
            
            # Build prompt
            context_parts = []
            if disease_context:
                normalized_context = disease_context
                if self._contains_tamil(disease_context):
                    translated_context = self._translate_text(disease_context, source="ta", target="en")
                    if translated_context and translated_context != disease_context:
                        normalized_context = f"{disease_context} (English: {translated_context})"
                context_parts.append(f"Disease detected: {normalized_context}")
            
            history_context = self.memory.get_context_string(session_id)
            if history_context:
                context_parts.append(f"Previous conversation:\n{history_context}")
            
            model_question = self._build_model_question(message, detected_language)
            context_parts.append(f"Farmer's question: {model_question}")
            full_prompt = "\n\n".join(context_parts)

            # Generate a complete response first so streamed output is not cut off.
            full_response = await self._get_complete_response(full_prompt, model_language)
            if response_language == LanguageEnum.TAMIL:
                translated_response = self._translate_long_text(full_response, source="en", target="ta")
                if translated_response.strip():
                    full_response = translated_response

            if not full_response.strip():
                raise Exception("Empty response generated")

            # Stream complete text in chunks to keep frontend behavior unchanged.
            chunk_size = 80
            for i in range(0, len(full_response), chunk_size):
                yield full_response[i:i + chunk_size]
                await asyncio.sleep(0.01)

            # Clean and store response
            full_response = clean_markdown_text(full_response)
            self.memory.add_message(session_id, "user", message)
            self.memory.add_message(session_id, "assistant", full_response)
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            active_lang = language or self._detect_language(message)
            fallback_response = self._get_provider_fallback_response(
                message=message,
                disease_context=disease_context,
                language=active_lang
            )

            chunk_size = 80
            for i in range(0, len(fallback_response), chunk_size):
                yield fallback_response[i:i + chunk_size]
                await asyncio.sleep(0.01)
    
    async def _get_complete_response(
        self,
        prompt: str,
        language: LanguageEnum
    ) -> str:
        """
        Get complete response with smart continuation logic.
        
        Args:
            prompt: Full prompt including context
            language: Response language
            
        Returns:
            Complete AI response
        """
        messages = [
            {"role": "system", "content": self._get_system_prompt(language)},
            {"role": "user", "content": prompt}
        ]
        
        final_answer = ""
        provider_model_plan = []

        if self.openrouter_enabled:
            for model_name in self.openrouter_model_candidates:
                provider_model_plan.append(("openrouter", model_name))

        if self.groq_enabled:
            for model_name in self.groq_model_candidates:
                provider_model_plan.append(("groq", model_name))

        if not provider_model_plan:
            raise Exception("No LLM provider configured")
        
        for i in range(self.max_continuation_loops):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = None
                    selected_provider = None
                    selected_model = None
                    last_status = None

                    for provider_name, model_name in provider_model_plan:
                        payload = {
                            "model": model_name,
                            "messages": messages,
                            "max_tokens": self.max_tokens,
                            "temperature": self.temperature
                        }

                        if provider_name == "openrouter":
                            request_url = f"{self.openrouter_base_url}/chat/completions"
                            request_headers = self.openrouter_headers
                        else:
                            request_url = f"{self.groq_base_url}/chat/completions"
                            request_headers = self.groq_headers

                        model_response = await client.post(
                            request_url,
                            headers=request_headers,
                            json=payload
                        )

                        if model_response.status_code == 200:
                            response = model_response
                            selected_provider = provider_name
                            selected_model = model_name
                            break

                        last_status = model_response.status_code
                        logger.warning(
                            f"Model failed: {provider_name}/{model_name} "
                            f"(status {model_response.status_code})"
                        )

                    if response is None:
                        logger.error(f"All models failed (last status: {last_status})")
                        if final_answer:
                            return clean_markdown_text(final_answer)
                        raise Exception("Server error. Please try again.")

                    if selected_model:
                        logger.info(
                            f"Chat response generated with provider/model: "
                            f"{selected_provider}/{selected_model}"
                        )
                    
                    result = response.json()
                    choices = result.get("choices", [])
                    if not choices:
                        logger.warning("Model returned no choices; trying continuation/retry")
                        continue

                    message_obj = choices[0].get("message", {}) or {}
                    answer = message_obj.get("content") or ""
                    finish_reason = choices[0].get("finish_reason", "")

                    # Some providers occasionally return empty content in a successful response.
                    # Do not crash; continue loop and request another completion chunk.
                    if not answer.strip():
                        logger.warning("Model returned empty content; requesting continuation")
                        messages.append({
                            "role": "user",
                            "content": "Continue from where you stopped and complete the answer. Do not repeat previous lines."
                        })
                        await asyncio.sleep(0.3)
                        continue

                    cleaned_answer = answer.strip()

                    if not final_answer:
                        final_answer = cleaned_answer
                    else:
                        # Avoid repeating near-duplicate continuation chunks.
                        lower_existing = final_answer.lower()
                        lower_new = cleaned_answer.lower()
                        if lower_new not in lower_existing:
                            final_answer = f"{final_answer} {cleaned_answer}".strip()

                    # Prefer one coherent answer; continue only when clearly truncated.
                    if finish_reason == "stop":
                        break

                    if finish_reason == "length" and is_sentence_complete(final_answer):
                        break

                    # Request a short, non-repeating continuation only if still incomplete.
                    messages.append({"role": "assistant", "content": cleaned_answer})
                    messages.append({
                        "role": "user",
                        "content": "Continue exactly where you stopped and complete the remaining answer in full sentences. Do not repeat earlier content."
                    })

                    await asyncio.sleep(0.3)
                    
            except httpx.TimeoutException:
                logger.warning(f"Timeout on attempt {i + 1}")
                if final_answer:
                    break
                raise Exception("Request timeout. Please try again.")
        
        cleaned = clean_markdown_text(final_answer).strip()
        return cleaned
    
    def _detect_language(self, text: str) -> LanguageEnum:
        """
        Detect language from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language enum
        """
        if self._contains_tamil(text):
            return LanguageEnum.TAMIL

        try:
            from langdetect import detect
            lang_code = detect(text)
            
            if lang_code == "ta":
                return LanguageEnum.TAMIL
            else:
                return LanguageEnum.ENGLISH
        except:
            return LanguageEnum.ENGLISH
    
    def clear_session(self, session_id: str):
        """Clear chat history for a session."""
        self.memory.clear_session(session_id)
        logger.info(f"Cleared session: {session_id}")


# Singleton instance
llm_service = LLMService()
