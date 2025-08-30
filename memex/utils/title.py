import re
from typing import List


def title_from_filename(slug: str, acronym_map: dict[str, str], 
                        lil_words: list[str]) -> str:
    """
    - splits on hyphens/underscores
    - Title Case tokens
    - applies acronym_map & little words overrides (case-insensitive keys)
    """
    slug_list = re.split("[-_]", slug.strip())
    process: List[str] = []
    
    for i, word in enumerate(slug_list):
        low = word.lower()
        if low in acronym_map:
            process.append(acronym_map[low])
        elif low in lil_words and i != 0: # don't lowercase first word
            process.append(low)
        else:
            process.append(low.capitalize())
    title = " ".join(process)

    return title

if __name__ == "__main__":

    lil_words = ["in", "on", "a", "the"]
    acronym_map = {
        "git": "Git",
        "cheatsheet": "CheatSheet",
    }

    title = title_from_filename("in-the_git-cheatsheet_initial-version-all-in-one", acronym_map, lil_words)
    print(title)