{pkgs ? import <nixpkgs> {}}:
with pkgs;
  mkShell {
    buildInputs = [
      python311Packages.virtualenv
      python311Packages.nltk
      python311Packages.pyspellchecker
      python311Packages.langdetect
      python311Packages.imbalanced-learn
      python311Packages.gensim
      python311Packages.beautifulsoup4
      python311Packages.sentence-transformers
      python311Packages.seaborn
      python311Packages.wikitextparser
    ];

    shellHook = ''
      if ! [ -e .venv ]; then
        python3 -m venv .venv
      fi
      source .venv/bin/activate


    '';
  }
