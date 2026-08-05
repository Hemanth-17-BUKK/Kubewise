import json
import re


def parse_llm_json(text: str):

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if not match:
        raise ValueError(
            "No JSON found in LLM response."
        )

    return json.loads(match.group(0))