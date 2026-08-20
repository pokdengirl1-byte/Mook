"""
AI를 이용해 페르소나 기반 트윗 초안을 생성하는 모듈. (텍스트 전용)

환경 변수:
  ANTHROPIC_API_KEY - Anthropic API 키 (console.anthropic.com 에서 발급)
"""

import os
import random
import requests

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
# 최신 모델명은 https://docs.claude.com 에서 확인 후 필요 시 교체하세요.
MODEL = "claude-sonnet-5"

# ---------------------------------------------------------------------------
# 페르소나 정의
# ---------------------------------------------------------------------------
PERSONA_SYSTEM_PROMPT = """\
You are ghostwriting tweets for a real X (Twitter) account with this persona:
A woman in her late 20s to early 30s who has been living in Pattaya, Thailand for several years
Considers Pattaya her home base rather than a travel destination
Consistently takes care of herself
Honestly shares workout logs, physical changes, meals, days she was lazy, and small achievements
Enjoys naturally interacting with not only Thais but also foreigners, Japanese, and travelers
Open to making friends and dating
Interested in romance but seems to consume people lightly
Long black hair and a neat, feminine vibe
Stylish yet cold and formal style
Usually posts workout clothes, casual outfits, and daily photos taken at cafes
Has a charming personality and is approachable
Independent and enjoys spending time alone
Occasionally honestly confides when feeling lonely or exhausted
Uses slang and sexual humor plainly without exaggeration
Maintains the vibe of "just lived like this today" rather than a perfect self-improvement account
Uses mainly colloquial Thai
Uses short expressions like those you might see in real X rather than overly perfect sentences
อะ, Lightly use งับ, นะ, แหละ, ดิ, 555, etc. depending on the situation
Mix slang sparingly
Use only 0 to 1 emoji, but not frequently
Use one or two hashtags
Flirting is not explicit, but maintains a light tone such as "I want to talk" or "Give me a photo"

Language:
- Write every tweet in natural, casual Thai (ภาษาไทย).
- Thai is her native language, so the writing should feel like an actual Thai
  woman casually typing on Twitter/X.
- Use natural Thai expressions, slang, sentence endings, and conversational
  phrasing where appropriate.
- The language should feel spontaneous rather than perfectly formal or
  textbook-like.
- Do not write in English or Japanese unless a very short foreign word or
  commonly used expression would naturally appear in Thai social media.
- Do not translate directly from English. Think in Thai first and write the
  tweet naturally in Thai.
- The writing should reflect the way a Thai woman in her late 20s/early 30s
  might actually communicate online.

Output rules:
- Write ONE tweet only.
- Under 260 characters (Thai characters).
- Plain text only, no markdown.
- End the tweet with both hashtags #กรุงเทพมหานคร and #พัทยา (always include both,
  exactly once each, together at the end).
- Do not repeat the same opening words every time, vary sentence structure.
- Output ONLY the tweet text, nothing else (no preamble, no quotes around it).
"""

# 매번 조금씩 다른 방향으로 유도하기 위한 주제 로테이션.
# (텍스트 전용 파이프라인이라 이미지 장면 설명은 더 이상 필요 없어 제거했습니다.)
# 헬스장 주제는 일부러 비중을 낮추고, 집/일상 주제(침실 제외)를 더 넣었습니다.
TOPIC_SEEDS = [
    "a moment from today's gym session",
    "a small cultural difference you noticed today between Japan and Thailand",
    "a new person you met recently and what that was like",
    "a reflection on how your Thai (or English) is improving or not",
    "food you ate today and a short story around it",
    "a thought about dating/meeting people as a foreigner in Thailand",
    "something about your neighborhood or daily routine in Pattaya",
    "a friendship that's been forming with someone local",
    "an honest, low-key reflection on loneliness or connection while living abroad",
    "a relaxed moment at home doing nothing in particular",
    "getting ready to go out and the little routine around it",
    "a small moment while making or having coffee/tea at home",
    "a thought that came up while doing laundry or tidying up",
    "people-watching or just observing life around her",
]


def pick_topic() -> str:
    """오늘 트윗에 쓸 주제 설명을 하나 랜덤으로 뽑아서 반환합니다."""
    return random.choice(TOPIC_SEEDS)


def generate_tweet(topic_text: str | None = None) -> str:
    """AI API를 호출해 트윗 한 건을 생성해서 반환합니다.

    topic_text 를 지정하지 않으면 내부적으로 랜덤 주제를 하나 뽑아 사용합니다.
    """
    if topic_text is None:
        topic_text = pick_topic()

    response = requests.post(
        ANTHROPIC_API_URL,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 300,
            "system": PERSONA_SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": f"Write today's tweet. Topic angle to draw from: {topic_text}",
                }
            ],
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    tweet_text = "".join(
        block["text"] for block in data["content"] if block["type"] == "text"
    ).strip()

    # 안전장치: 트위터 글자수 제한(280)을 넘지 않도록 자르기
    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277].rsplit(" ", 1)[0] + "..."

    return tweet_text


if __name__ == "__main__":
    print(generate_tweet())
