# %% [markdown]
# # LLM-agent pilot on Kaggle (Ollama)
#
# Feasibility check only: are the model's replies usable, how many seconds does one agent
# decision take, and does the model behave sensibly. It plays a few rounds on VALIDATION
# scenarios. Its numbers are not experimental results.
#
# Before running:
# 1. Settings -> Internet: **On** (needs a phone-verified Kaggle account).
# 2. Settings -> Accelerator: **GPU T4 x2**.
# 3. Add Input -> the dataset made from the latest `project_bundle.zip` (and only that one).
# Then: Run All (about 30 minutes; keep the tab open). When it finishes, download `/kaggle/working/pilot_output.zip` from the
# Output panel and give it to Claude Code.

# %%
MODELS = ["qwen2.5:7b"]     # the model frozen in the protocol
DOMAINS = ["pharma", "energy"]
ROUNDS = 20                 # 20 rounds x 5 agents x 2 systems = 200 agent decisions per run
PARALLEL = 5                # the five agents of a round are asked at the same time
# Pilot 4: the prompt gives the tool's raw numbers only (no truthful explanation), under two
# weights of the private gain: 0.5 (natural) and 0.75 (higher private gain).
CONDITIONS = [("natural", 0.5), ("higher_gain", 0.75)]

# %%
import glob
import os
import shutil
import subprocess
import time
import zipfile

# Kaggle usually unpacks an uploaded zip, so accept either the zip or its unpacked folder.
bundles = glob.glob("/kaggle/input/**/project_bundle.zip", recursive=True)
unpacked = glob.glob("/kaggle/input/**/run_experiment.py", recursive=True)
assert bundles or unpacked, "Attach the dataset made from project_bundle.zip (Add Input)."
WORK = "/kaggle/working/project"
shutil.rmtree(WORK, ignore_errors=True)
if unpacked:
    shutil.copytree(os.path.dirname(unpacked[0]), WORK)
else:
    with zipfile.ZipFile(bundles[0]) as archive:
        archive.extractall(WORK)
os.chdir(WORK)
assert "--prompt" in open("experiments/llm_pilot.py").read(), "This dataset is an old bundle."
print("project bundle is the pilot-4 version")

# %%
# The pinned versions are for the original environment; Kaggle's own versions are used here
# and recorded, because the pilot only checks feasibility.
import numpy, pandas, scipy, shap, sklearn  # noqa: E401,E402

print({m.__name__: m.__version__ for m in (numpy, pandas, sklearn, shap, scipy)})
print(subprocess.run("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader",
                     shell=True, capture_output=True, text=True).stdout or "no GPU: CPU run")

# %%
subprocess.run("apt-get install -y -qq zstd pciutils > /dev/null 2>&1", shell=True)
subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)
server = subprocess.Popen(["ollama", "serve"], stdout=open("/kaggle/working/ollama.log", "w"),
                          stderr=subprocess.STDOUT,
                          env={**os.environ, "OLLAMA_NUM_PARALLEL": str(PARALLEL)})
time.sleep(8)
for model in MODELS:
    subprocess.run(["ollama", "pull", model], check=True)
print(subprocess.run(["ollama", "list"], capture_output=True, text=True).stdout)

# %%
# Pilot 4: raw tool output, the agent works out its own explanation.
for domain in DOMAINS:
    for model in MODELS:
        for label, omega in CONDITIONS:
            subprocess.run(["python", "-m", "experiments.llm_pilot", "--domain", domain,
                            "--model", model, "--rounds", str(ROUNDS),
                            "--workers", str(PARALLEL), "--prompt", "raw",
                            "--omega", str(omega), "--tag", f"_p4_{label}",
                            "--output-dir", "/kaggle/working/pilot"], check=True)

# %%
shutil.copy("/kaggle/working/ollama.log", "/kaggle/working/pilot/ollama.log")
shutil.make_archive("/kaggle/working/pilot_output", "zip", "/kaggle/working/pilot")
print("Download /kaggle/working/pilot_output.zip from the Output panel.")
