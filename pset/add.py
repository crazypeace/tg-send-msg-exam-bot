import random

def buildQA():
  num1 = random.randint(1, 10)
  num2 = random.randint(1, 10)
  question = f"{num1} + {num2} = ?"
  correct_answer = str(num1 + num2)

  return question, correct_answer