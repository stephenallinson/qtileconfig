import random

VENT = """
VENT

Write what makes you angry.

I don't know what I think until I write it.
"""
OBLIGATIONS = """
OBLIGATIONS

Make sure that obligations are ordered, and not chaos in your mind.
Don't use your brain to store problems, use it to solve problems.

Obligation Dump:
    Anything that could remotely be considered an obligation.
    From the mundane to the grandiose.

Organize:
    Use buckets like family, work, personal, etc.

Prioritize:
    Ask one question: "Does it make the boat for faster?

Bare Minimum:
    What is the bare minimum to make tomorrow suck less, do that?
"""
MINDSET = """
MINDSET

Your mindset is like the operating system of your brain, and
can be improved.

Reframing:
    How is this the best thing that has ever happened to me?

Possibility:
    Gather evidence that we are what we want to be.
    Use an identity statement, and then write out the 'because'.

Inversion:
    Practicing a reaction to a situation looking at it from the solution,
    and the opposite of the solution.

Persepctive:
    Approach the issue as if you are observing it as your friend. What
    advice would you give?.

Discipline:
    Be proud of practicing when you don't want to.

Gratitude:
    1. Something mundane
    2. Something that happened by chance
    3. Something that you made happen.
"""
IDEATE = """
IDEATE

Coming up with solutions to a proble you're trying to solve.

Timer:
    Come up with 30 answers before the timer goes off.

Quantity:
    Don't edit the list until you're done.

Examples:
    How would a subject matter expert solve the issue?

Close the loop:
    Write down the question, and your brain will try to close the loop.
"""
TRAJECTORY = """
TRAJECTORY

Where are you going, and how are you going to get there?

Direction:
    What is your goal?
    Are you moving away from the goal, or towards the goal?

Day-To-Day:
    Find the hidden metrics and make them visible.

Three questions:
    1. What excited me?
    2. What drained me of energy?
    3. What did I learn?
"""


def journal_prompt(random):
    vomit = [VENT, OBLIGATIONS, MINDSET, IDEATE, TRAJECTORY]
    return vomit[random]


if __name__ == "__main__":
    journal_prompt(random.randint(0, 4))
