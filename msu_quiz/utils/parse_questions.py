import re

regex3 = r"(^(?:\s*(?:\(*[a-zA-Z]\)*\.*\s+)))"
regex4 = r"(^\s*\d+[\.\)\s]\s+)"
regex5 = r"(^[a-fA-F][\)\.]\s+[\s\S]+)"
regex6 = r"(^(?!(^[a-zA-Z][\)\.]\s+[\s\S]+)).*)"
regex1 = r"(^[\t ]*[0-9]+[\)\.][\t ]+[\s\S]*?(?=^[\n\r]))"


def parse_questions(question_answer):
    matches = re.finditer(regex1, question_answer, re.MULTILINE)
    quiz_list = []

    for match in matches:
        question = " ".join(
            [x[0] for x in re.findall(regex6, match.group(0), re.MULTILINE)])
        answer = " ".join(re.findall(regex5, match.group(0), re.MULTILINE))
        answer = re.sub(regex3, '', answer, 0,
                        re.MULTILINE).splitlines()
        mcqs = answer
        quiz_list.append(
            dict(question=re.sub(regex4, '', question),
                 answer=answer[0],
                 mcqs=mcqs))
    return quiz_list
