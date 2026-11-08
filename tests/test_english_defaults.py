import re

from core.audio.subtitle import SubtitleGenerator
from core.config import AVAILABLE_VOICES, DEFAULT_VOICE
from core.pipelines.creative_video import _narration_char_limit
from core.pipelines.manuscript_video import (
    _SENTENCE_END_RE,
    _estimate_speech_seconds,
)
from models.task import AudioConfig


def test_english_is_the_default_voice():
    assert DEFAULT_VOICE == "en-US-GuyNeural"
    assert AudioConfig().voice == DEFAULT_VOICE
    assert len(AVAILABLE_VOICES) == 5
    assert all(voice["id"].startswith("en-US-") for voice in AVAILABLE_VOICES)


def test_manuscript_splits_english_sentences():
    parts = [part.strip() for part in _SENTENCE_END_RE.split("First sentence. Second sentence! Third?") if part.strip()]
    assert parts == ["First sentence.", "Second sentence!", "Third?"]


def test_speech_duration_estimates_english_by_words_and_cjk_by_characters():
    assert _estimate_speech_seconds("One two three four five") == 2.0
    assert _estimate_speech_seconds("你好世界") == 1.0


def test_creative_narration_budget_is_language_aware():
    assert _narration_char_limit(10, "English narration") == 150
    assert _narration_char_limit(10, "中文旁白") == 40


def test_long_english_subtitles_break_on_word_boundaries():
    text = "This is a deliberately long English sentence that should be split into several readable subtitle groups without cutting words apart."
    srt_content = SubtitleGenerator._generate_scene_aware_srt([text], [12.0])
    captions = [
        block.splitlines()[2]
        for block in srt_content.strip().split("\n\n")
        if block.strip()
    ]
    assert len(captions) > 1
    assert " ".join(captions).replace("  ", " ") == text
    assert all(len(caption) <= 38 for caption in captions)
