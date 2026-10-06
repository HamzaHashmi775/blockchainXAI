# %% [markdown]
# # LLM-agent pilot on Kaggle (Ollama)
#
# Feasibility check only: are the model's replies usable, how many seconds does one agent
# decision take, and does the model behave sensibly. It plays a few rounds on VALIDATION
# scenarios. Its numbers are not experimental results.
#
# Before running:
# 1. Settings -> Internet: **On** (needs a phone-verified Kaggle account).
# 2. Settings -> Accelerator: **GPU T4 x2** if you have GPU quota; otherwise leave it on
#    CPU and set MODELS below to one small model.
# 3. Add Input -> your uploaded dataset that contains `project_bundle.zip`.
# Then: Run All. When it finishes, download `/kaggle/working/pilot_output.zip` from the
# Output panel and give it to Claude Code.

# %%
MODELS = ["qwen2.5:7b", "llama3.1:8b"]   # on CPU use one small model, e.g. ["qwen2.5:3b"]
DOMAINS = ["pharma"]        # add "energy" to pilot the second case study as well
ROUNDS = 10                 # 10 rounds x 5 agents x 2 systems = 100 agent decisions per run
PARALLEL = 5                # the five agents of a round are asked at the same time

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
print(sorted(os.listdir(WORK)))

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
# Each model is run one request at a time and then with the five agents asked together,
# to measure the speed-up and to check that the answers do not change.
for domain in DOMAINS:
    for model in MODELS:
        for workers, tag in ((1, "_seq"), (PARALLEL, "_par")):
            subprocess.run(["python", "-m", "experiments.llm_pilot", "--domain", domain,
                            "--model", model, "--rounds", str(ROUNDS),
                            "--workers", str(workers), "--tag", tag,
                            "--output-dir", "/kaggle/working/pilot"], check=True)

# %%
shutil.copy("/kaggle/working/ollama.log", "/kaggle/working/pilot/ollama.log")
shutil.make_archive("/kaggle/working/pilot_output", "zip", "/kaggle/working/pilot")
print("Download /kaggle/working/pilot_output.zip from the Output panel.")
