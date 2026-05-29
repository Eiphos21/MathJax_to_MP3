import time
import re
import os
import subprocess
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from gtts import gTTS

# Configuration
URL          = "http://your-webpage-here"
START_MARKER = "start"
END_MARKER   = "end"
OUTPUT_FILE  = "output"

# Find Speech Rule Engine
sre_path = shutil.which("sre")
if not sre_path:
    raise FileNotFoundError("SRE not found")

# Launch headless Chrome and load page
options = webdriver.ChromeOptions()
for arg in ["--headless", "--no-sandbox", "--disable-dev-shm-usage"]:
    options.add_argument(arg)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Loads the page
driver.get(URL)
time.sleep(10) 
driver.execute_script("return MathJax.startup.promise")

# Extract MathML and replace with placeholders
mathml_list = driver.execute_script("""
  const mathElements = Array.from(document.querySelectorAll("mjx-container, script[type^='math/']"));
  const mathList = [];

  mathElements.forEach((el, index) => {
    const placeholderText = `[[MATH_${index}]]`;
    const placeholderNode = document.createTextNode(placeholderText);
    el.parentNode.replaceChild(placeholderNode, el);
    mathList.push(el.outerHTML);
  });

  return mathList;
""")

# Extract readable text content
script_parts = driver.execute_script("""
  const tags = Array.from(document.querySelectorAll("p, li, h1, h2, h3, div.callout-title-container.flex-fill, div.title, div.quarto-title-meta-heading, div.quarto-title-meta-content, div.abstract, div.summary, div.quarto-category, span.author, div.author, div.abstract-title, div.categories"));

  const uniqueTags = tags.filter((el, i, arr) => {
    return !arr.some(otherEl => otherEl !== el && otherEl.contains(el));
  });

  const output = [];
  uniqueTags.forEach(el => {
    const text = el.innerText.trim();
    if (text) output.push(text);
  });

  return output;
""")

# Close browser
driver.quit()

# Convert MathML to spoken text using SRE 
spoken_math = []
for i, mathml in enumerate(mathml_list):
    try:
        mathml_clean = mathml.split('<mjx-assistive-mml')[1].split('</mjx-assistive-mml>')[0]
        mathml_clean = re.sub(r'mathvariant="[^"]*"', '', mathml_clean)
        
        result = subprocess.run(
            [sre_path, "--speech", "--domain", "clearspeak"],
            input=mathml_clean.encode("utf-8"),  # Pass the MathML as input to SRE
            capture_output=True
        )

        spoken = result.stdout.decode("utf-8").strip()  # Get the spoken math output
        if spoken:
            spoken_math.append(spoken)  
        else:
            spoken_math.append("(Empty output)")  
    except Exception as e:

        spoken_math.append(f"(Error: {e})") 

# Rebuild text with spoken math inserted
final_script = []
for part in script_parts:
    for i, spoken in enumerate(spoken_math):
        part = part.replace(f"[[MATH_{i}]]", spoken)
    final_script.append(part)

# Save the final script with spoken math
with open("final_script_with_translated_math.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(final_script))


# Open the file to read the script
with open("final_script_with_translated_math.txt", "r", encoding="utf-8") as f:
    script = f.read()

match = re.search(rf"{re.escape(START_MARKER)}(.*?){re.escape(END_MARKER)}", script, re.DOTALL)

if not match:
    raise ValueError(f"Could not find content")

with open(f"{OUTPUT_FILE}.txt", "w", encoding="utf-8") as f:
    f.write(match.group(0))

print(f"Saved to {OUTPUT_FILE}.txt")

# Convert to speech
print("Processing...")

with open(f"{OUTPUT_FILE}.txt", "r", encoding="utf-8") as f:
    text = f.read()
    
text = text.lower()
gTTS(text).save(f"{OUTPUT_FILE}.mp3")

print(f"Saved to {OUTPUT_FILE}.mp3")
