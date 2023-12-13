# MarketMingle-Analytics

### Demystify the Market: Your Path to Effortless Company Comparisons!


# ABOUT
visit the web version of this app under https://marketmingleanalytics.streamlit.app/

be advised that the AI feature has been removed in the web version

the full code for local deployment can be found in the /MarketMingle_Analytics_for_local_use folder

# STRUCTURE
one respective file that handles the visuals for the subpage and two helper files (data_loader.py & general_worker.py) to handle data operations and data pulls

the code has all basic functionalities to add a secondary search for private companies incase the public company search does not return any results, at the moment not in use

# CREDITS
for CSS & HTML code parts in a streamlit.markdown(allow_unsafe_html=True) context we relied on ChatGPT

# APPEARANCE
The App is set to always start up in its dark theme (via the .streamlit/config.toml file), we chose to solely rely on the dark theme as streamlit currently does not offer to dynamically fetch the current theme used, so non-streamlit parts, like all charts in this app, can not be adjusted to the theme and therefore a different theme would distort the user interface. 
Therefore users are advised to not change the theme in the apps settings, a possibility we unfortunately can't prevent

# HOW TO: RUN LOCALLY
For optimal use and to take advantage of all functonalities please run the streamlit application locally on your machine. To achieve this follow these steps:
1. Download the ..._for_local_use folder from this repository. It is easiest to simply download the whole repository and disregard the other contents. Find further information on how to download the repositry here https://blog.hubspot.com/website/download-from-github
2. Navigate to the downloaded folder, specifically the ..._for_local_use folder using the terminal/cmd. Find more information on how to here: https://www.digitalcitizen.life/command-prompt-how-use-basic-commands/
3. Now run `pip install -r requirements.txt`
4. Next run `streamlit run main.py`
5. Now the App should automatically start up in your browser
