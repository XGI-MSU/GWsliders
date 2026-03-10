## How to Access and Use this Notebook:

You will need Python 3.11 installed. To check if you already have it, open your terminal and run:
```
python3.11 --version
```
If you see `Python 3.11.x`, you are good to go. If not, download it from https://www.python.org/downloads/

> Python 3.12 may also work — if you only have 3.12, try replacing `python3.11` with `python3.12` in all commands below.
---

### Step 1: Open your terminal

- **Mac:** Press `Command + Space`, type `Terminal`, press Enter
- **Windows:** Press the Windows key, type `cmd`, press Enter

---

### Step 2: Choose where to put the project

Decide which folder you want the project to live in. 
For example, if you want it on your Desktop:

**Mac:**
```
cd ~/Desktop
```
**Windows:**
```
cd %USERPROFILE%\Desktop
```
Type one of the above and press Enter. You can replace `Desktop` with any folder you want, for example `cd ~/Documents`.

---

### Step 3: Clone the repository

Copy and paste the following into your terminal and press Enter:
```
git clone https://github.com/XGI-MSU/GWsliders.git
```
This will create a folder called `GWsliders` wherever you are. Now navigate into it:
```
cd GWsliders
```

---

### Step 4: Set up the environment

This installs all the software the notebook needs. Copy and paste these one line at a time, pressing Enter after each one.

**Mac/Linux:**
```
python3.11 -m venv gwslider-env
source gwslider-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name gwslider-env --display-name "Python (gwslider-env)"
```

**Windows:**
```
python3.11 -m venv gwslider-env
gwslider-env\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name gwslider-env --display-name "Python (gwslider-env)"
```

> ⚠️ The `pip install -r requirements.txt` step may take a few minutes — this is normal.

---

### Step 5: Open the notebook

Copy and paste the following and press Enter:
```
jupyter notebook
```
A browser window will open. Click on **[interactive_notebook].ipynb** to open it.

---

### Step 6: Select the correct kernel

In the top right corner of the notebook, you will see a kernel name. It should say `Python (gwslider-env)`.

- If it does not, click on it, select `Python (gwslider-env)` from the list, and click **Select**

---

### Step 7: Run the notebook

In the top menu, click **Kernel → Restart Kernel and Run All Cells**

---

### ⚠️ Every time you reopen the notebook

You will need to reactivate the environment before running `jupyter notebook`. In your terminal:

**Mac/Linux:**
```
source gwslider-env/bin/activate
```
**Windows:**
```
gwslider-env\Scripts\activate
```
Then repeat Step 5.
