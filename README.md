## How to Access and Use this Notebook:

You will need Python 3.11 installed. To check if you already have it, open your terminal and run:
```
python3.11 --version
```
If you see `Python 3.11.x`, you are good to go. If not, download it from https://www.python.org/downloads/

---
### Step 1: Choose where to put the project

Decide which folder you want the project to live in. 
For example, if you want it on your Desktop:

**Mac:**
```
cd Desktop
```
**Windows:**
```
cd %USERPROFILE%\Desktop
```
You can replace `Desktop` with any folder you want, for example `cd Documents`.

---

### Step 2: Clone the repository

Copy and paste the following into your terminal:
```
git clone https://github.com/XGI-MSU/GWsliders.git
```
This will create a folder called `GWsliders` wherever you are. Now navigate into it:
```
cd GWsliders
```

---

### Step 3: Set up the environment

Run the setup script — this will automatically create the environment and install everything the notebook needs:

**Mac/Linux:**
```
bash setup.sh
```
**Windows:**
```
python3.11 -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name=gwslider-env --display-name "gwslider-env"
```

> ⚠️ The install step may take a few minutes — this is normal.

---

### Step 4: Activate the environment and open the notebook

**Mac/Linux:**
```
source .venv/bin/activate
jupyter notebook
```
**Windows:**
```
.venv\Scripts\activate
jupyter notebook
```
A browser window will open. Click on **[interactive_notebook].ipynb** to open it.

---

### Step 5: Select the correct kernel

In the top right corner of the notebook, you will see a kernel name. It should say `gwslider-env`.

- If it does not, click on it, select `gwslider-env` from the list, and click **Select**

---

### Step 6: Run the notebook

In the top menu, click **Kernel → Restart Kernel and Run All Cells**

---

### ⚠️ Every time you reopen the notebook

You will need to reactivate the environment before running `jupyter notebook`. In your terminal:

**Mac/Linux:**
```
source .venv/bin/activate
jupyter notebook
```
**Windows:**
```
.venv\Scripts\activate
jupyter notebook
```
Then repeat Step 5.
