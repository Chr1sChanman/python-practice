"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob

class DocuBot:
    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()  # List of (filename, text)

        # Build a retrieval index (implemented in Phase 1)
        self.index = self.build_index(self.documents)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)
        """
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                docs.append((filename, text))
        return docs

    # -----------------------------------------------------------
    # Index Construction (Phase 1)
    # -----------------------------------------------------------

    def _normalize(self, word):
        """
        Normalize a single word by stripping a trailing 's' from words longer
        than 3 characters.

        This provides basic handling of plurals and present-tense verb forms so
        that query words and document words meet in the same canonical form:
            columns  -> column
            tables   -> table
            returns  -> return

        Words of 3 characters or fewer are left unchanged to avoid mangling
        short words like 'has' or 'was'.
        """
        if len(word) > 3 and word.endswith("s"):
            return word[:-1]
        return word

    def build_index(self, documents):
        """
        Build an inverted index mapping normalized, lowercase words to the
        documents they appear in.

        Each token is stripped of surrounding punctuation, lowercased, and
        passed through _normalize before being stored. This ensures the index
        keys use the same form as the query tokens looked up in retrieve().

        Example structure:
        {
            "token": ["AUTH.md", "API_REFERENCE.md"],
            "database": ["DATABASE.md"]
        }
        """
        index = {}
        for filename, text in documents:
            for token in text.split():
                word = self._normalize(token.strip(".,!?;:").lower())
                if not word:
                    continue
                if word not in index:
                    index[word] = []
                if filename not in index[word]:
                    index[word].append(filename)
        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval (Phase 1)
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        Return a numeric relevance score for how well text matches the query.

        Approach:
        - Tokenize and normalize both the query and the text the same way
          (strip punctuation, lowercase, apply _normalize).
        - Filter stopwords from the query so common words like 'the', 'is',
          and 'for' do not inflate scores for unrelated documents.
        - Count how many times each meaningful query word appears in the
          normalized text word list and sum the counts.

        A score of 0 means no meaningful query words were found in the text.
        Higher scores indicate more overlap.
        """
        stopwords = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "do", "does", "did", "for", "in", "of", "to", "on", "at",
            "by", "with", "this", "that", "it", "its", "i", "my", "we",
            "our", "any", "there", "how", "what", "which", "where", "or",
            "and", "not", "no", "if", "from", "as", "about", 
        }
        text_words = [
            self._normalize(t.strip(".,!?;:").lower())
            for t in text.split()
            if t.strip(".,!?;:")
        ]
        score = 0
        for token in query.split():
            word = self._normalize(token.strip(".,!?;:").lower())
            if word and word not in stopwords:
                score += text_words.count(word)
        return score

    def retrieve(self, query, top_k=3):
        """
        Return the top_k most relevant paragraphs for the given query.

        Steps:
        1. Normalize query tokens and look each one up in the inverted index to
           collect candidate filenames (documents that contain at least one
           query word).
        2. Split each candidate document into paragraphs on blank lines so that
           scoring operates on small, focused chunks rather than whole files.
        3. Score every paragraph with score_document and sort descending.
        4. Guardrail: if the highest score is 0 (no meaningful query words
           matched anything), return an empty list so the caller can respond
           with a refusal instead of returning irrelevant content.

        Returns a list of (filename, paragraph_text) tuples.
        """
        candidates = set()
        for token in query.split():
            word = self._normalize(token.strip(".,!?;:").lower())
            if word in self.index:
                candidates.update(self.index[word])

        doc_map = {filename: text for filename, text in self.documents}

        scored = []
        for filename in candidates:
            paragraphs = [p.strip() for p in doc_map[filename].split("\n\n") if p.strip()]
            for paragraph in paragraphs:
                score = self.score_document(query, paragraph)
                scored.append((score, filename, paragraph))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Guardrail: return nothing if the best match has zero overlap with the query
        if not scored or scored[0][0] == 0:
            return []

        results = [(filename, text) for _, filename, text in scored]
        return results[:top_k]

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3):
        """
        Phase 1 retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        formatted = []
        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        Phase 2 RAG mode.
        Uses student retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        return self.llm_client.answer_from_snippets(query, snippets)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive 'generation only' baselines.
        """
        return "\n\n".join(text for _, text in self.documents)
