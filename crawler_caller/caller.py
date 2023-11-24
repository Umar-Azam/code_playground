# %%

def generate_config(url : str, match : str, num_pages : int) :
    return (f'''import {{ Config }} from "./src/config";

export const defaultConfig: Config = {{
  url: "{url}",
  match: "{match}",
  maxPagesToCrawl: {num_pages},
  outputFileName: "../data/output.json",
}};''')

# Example url : https://www.builder.io/c/docs/developers
# Example match : https://www.builder.io/c/docs/**

with open('testconfig.ts','w') as file:
    file.write(generate_config('123','345',10))

# %%
