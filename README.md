# Gottlieb_Disney

For my case study, I selected the dash-gpt3-lines example. I modified this example to be able to show the user how the wait times change over time for different rides, or tell them the average wait time on a particular day, season or time. 

I downloaded wait times from: https://touringplans.com/walt-disney-world/crowd-calendar#DataSets
I selected two rides to start with, one from Animal Kingdom and one from Epcot. I cleaned and combined the data (see the Jupyter Notebook) and then modified the prompt in the app. 

Future work/other ideas:
1. More testing with plotting and average requests
2. Outlier detection
3. Use time series analysis to more accurately predict the wait time




In order to obtain access to the GPT-3 API, you will need to [join the waitlist](https://beta.openai.com/). Once you have the API,  you can find the secret key in [the quickstart](https://beta.openai.com/developer-quickstart), and export it as an environment variable:
```
export OPENAI_KEY="xxxxxxxxxxx"
```
Where "xxxxxxxxxxx" corresponds to your secret key.

## Instructions

To get started, first clone this repo:
```
git clone https://github.com/plotly/dash-sample-apps.git
cd dash-sample-apps/apps/dash-gpt3-bars
```

Create a conda env:
```
conda create -n dash-gpt3-bars python=3.7.6
conda activate dash-gpt3-bars
```

Or a venv (make sure your `python3` is 3.6+):
```
python3 -m venv venv
source venv/bin/activate  # for Windows, use venv\Scripts\activate.bat
```

Install all the requirements:

```
pip install -r requirements.txt
```

You can now run the app:
```
python app.py
```

and visit http://127.0.0.1:8050/.
