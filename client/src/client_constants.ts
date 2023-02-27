export const spacy_version = "3.4.4";
export const pygls_version = "1.0.0";
export const python_args = pygls_version + " " + spacy_version;

export const errors = {
  E001: "[E001] Python Extension not installed ",
  E002: "[E002] Selected python interpreter path does not exist: ",
  E003: "[E003] Missing modules to run spaCy Extension: ",
  E004: "[E004] Module versions not compatible: ",
  E005: "[E005] Error when using python interpreter: ",
  E006: "[E006] Module pygls not found ",
  E007: "[E007] Module spaCy not found ",
  E008:
    "[E008] Version of pygls not compatible. Please make sure your pygls version is >=" +
    pygls_version,
  E009:
    "[E009] Version of spaCy not compatible. Please make sure your spaCy version is >=" +
    spacy_version,
};

export const warnings = {
  W001: "[W001] Please select a python interpreter ",
};

export const infos = {
  I001: "[I001] spaCy Extension started ",
  I002: "[I002] spaCy Extension stopped ",
  I003: "[I003] Python interpreter compatible: ",
};

export const status = {
  S001: "spaCy Extension active on: ",
  S002: "spaCy Extension not active. Please select Python interpreter.",
  S003: "Selected python interpreter not compatible. See the output for more information.",
};
