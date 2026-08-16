import torch
import torch.nn as nn


class BiLSTMClassifier(nn.Module):
    """Bidirectional LSTM binary classifier.

    Concatenates the final hidden states from both directions and feeds
    them through a linear layer.  If pre-trained embeddings are supplied
    they're loaded but left unfrozen so fine-tuning can adjust them.
    """

    def __init__(self, vocab_size, embedding_dim, hidden_dim,
                 output_dim=1, embeddings=None):
        super().__init__()

        if embeddings is not None:
            self.embedding = nn.Embedding.from_pretrained(embeddings, freeze=False)
        else:
            self.embedding = nn.Embedding(vocab_size, embedding_dim)

        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=1,
                            bidirectional=True, batch_first=True)
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)

    def forward(self, x, lengths):
        embedded = self.embedding(x)
        packed = nn.utils.rnn.pack_padded_sequence(
            embedded, lengths, batch_first=True, enforce_sorted=False)
        _, (hidden, _) = self.lstm(packed)
        hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)
        return self.fc(self.dropout(hidden)).view(-1)
