import unittest
from rag.indexer import RAGIndexer
from rag.parser import document_parser

class TestRAG(unittest.TestCase):
    def test_text_chunking(self):
        indexer = RAGIndexer(chunk_size=10, chunk_overlap=2)
        text = "abcdefghijk" # length 11
        # Chunks:
        # 1. 0:10 (abcdefghij) -> next starts at 10 - 2 = 8
        # 2. 8:11 (ijk)
        chunks = indexer._chunk_text(text)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0], "abcdefghij")
        self.assertEqual(chunks[1], "ijk")

    def test_unknown_file_parser_fallback(self):
        # Passing an unknown file extension should fallback to plain text reader
        content = document_parser.parse("nonexistent_file.xyz")
        # Should return the error string from read_text_file
        self.assertTrue("[ERROR] Could not read file" in content or "FileNotFoundError" in content)

if __name__ == "__main__":
    unittest.main()
