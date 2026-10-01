"""The three stages that turn a document into detector input.

    document -> format classification -> role-labelled outline -> de-leak paraphrase

Run them in order. Each writes one JSON file per document so a job that dies at
90% resumes from what already landed rather than restarting.
"""
