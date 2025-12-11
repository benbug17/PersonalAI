"""
Groq LLM client module for voice learning assistant.
Handles chat completions using Groq's API with llama-3.1-8b-instant model.
"""

import os
from typing import Optional
from groq import Groq


def get_groq_client() -> Optional[Groq]:
    """
    Initialize and return a Groq client instance.

    Returns:
        Groq client if API key is available, None otherwise
    """
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    return Groq(api_key=api_key)


def get_completion(
    user_query: str,
    system_prompt: Optional[str] = None,
    model: str = "llama-3.1-8b-instant",
    max_tokens: int = 1024,
    temperature: float = 0.7
) -> Optional[str]:
    """
    Get a chat completion from Groq LLM.

    Args:
        user_query: User's question or prompt
        system_prompt: Optional system prompt to set context
        model: Model to use (default: llama-3.1-8b-instant)
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature (0.0 to 2.0)

    Returns:
        Assistant's response text, or None if request fails
    """
    client = get_groq_client()

    if not client:
        return None

    try:
        # Build messages array
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        # Add user query
        messages.append({
            "role": "user",
            "content": user_query
        })

        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )

        # Extract response
        response = chat_completion.choices[0].message.content
        return response

    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return None


def get_learning_assistant_response(user_query: str) -> Optional[str]:
    """
    Get a response from the learning assistant.
    Uses a specialized system prompt for educational assistance.

    Args:
        user_query: User's learning question

    Returns:
        Assistant's educational response, or None if request fails
    """
    system_prompt = """You are a helpful voice-first learning assistant. Your role is to:
- Provide clear, concise explanations suitable for voice interaction
- Break down complex topics into simple, understandable parts
- Use examples and analogies to aid understanding
- Encourage curiosity and further learning
- Keep responses conversational and engaging
- Limit responses to 2-3 paragraphs for voice delivery

Always be patient, supportive, and adapt your explanations to the learner's needs."""

    return get_completion(
        user_query=user_query,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=512
    )
