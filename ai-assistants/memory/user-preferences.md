# User Preferences

Behavioral overrides expressed by the user. These take priority over all provider and agent file instructions. These persist across sessions so agents don't re-ask decided preferences.

YOU MUST ASK one or all of following questions (depending on the need and relevance) and CONFIRM WITH USER always before making an entry to this file:
Questions to be asked to user:

QUESTION-1: Is this <preference/suggestion/ask> a one time suggestion/ask (option-1) or would you like to see it followed in all future actions (option-2)?

QUESTION-2: Is this <preference/suggestion/ask> just for current working agent (option -1), or should it be followed by all the agents working on this task in future also (option-2)? 

You can add more questions if needed or relevant.

**MANDATORY Format for the preferences to be written to this file**: Each entry has a date, the preference, and the original user quote.

---

<!-- Example entries (remove these and replace with actual preferences):

### YYYY-MM-DD 
**Preference**: <Write preference statement here>.
**User said**: <Write exact statement from user here for asking this preference.>

-->

### 2026-03-08 
**Preference**: After completing development of any user task, the command or script to run the task MUST BE SINGLE LINE command. User MUST NEVER BE ASKED to do any additional manual step in order to run it. For e.g., if the application is web app then opening the browser must also by done by the run script. DO NOT ASK USER to open the browser manually. RUN command MUST BE A SINGLE COMMAND capable of running the application.
**User said**: "Your run script or command should be a single line command for me. Please never ask me to do any manual step in order to run the application."

### 2026-03-08 
**Preference**: All the agents MUST ANNOUNCE THEMSELVES before starting their step or task.
**User said**: "I did not see IT-agent come-in after product-owner agent. All the agents, please always ANNOUNCE YOURSELVES, and then start to do your work."

### 2026-03-08 
**Preference**: If running the created application needs a port, then add command in the run script to first check if port is available, if not, then start it on another available port.
**User said**: "Please look for availability of the port before running the created application. Run on available port only."