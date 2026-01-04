import torch
import torch.nn as nn
import torch.nn.functional as F

class DigitCNN(nn.Module):
    """数字認識CNN"""
    def __init__(self):
        super(DigitCNN, self).__init__()

        # Conv層
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)

        # プーリング
        self.pool = nn.MaxPool2d(2, 2)

        # 全結合層
        self.fc1 = nn.Linear(32 * 7 * 7, 64)
        self.fc2 = nn.Linear(64, 10)

        # Dropout
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        # x: [batch, 1, 28, 28]
        x = self.pool(F.relu(self.conv1(x)))  # [batch, 16, 14, 14]
        x = self.pool(F.relu(self.conv2(x)))  # [batch, 32, 7, 7]
        x = x.view(-1, 32 * 7 * 7)             # [batch, 1568]
        x = F.relu(self.fc1(x))                # [batch, 64]
        x = self.dropout(x)
        x = self.fc2(x)                        # [batch, 10]
        return x

class DigitVAE(nn.Module):
    """数字生成VAE"""
    def __init__(self, latent_dim=16):
        super(DigitVAE, self).__init__()

        self.latent_dim = latent_dim

        # Encoder
        self.enc_conv1 = nn.Conv2d(1, 16, 3, stride=2, padding=1)  # 28x28 -> 14x14
        self.enc_conv2 = nn.Conv2d(16, 32, 3, stride=2, padding=1) # 14x14 -> 7x7

        self.fc_mu = nn.Linear(32 * 7 * 7, latent_dim)
        self.fc_logvar = nn.Linear(32 * 7 * 7, latent_dim)

        # Decoder
        self.fc_decode = nn.Linear(latent_dim, 32 * 7 * 7)
        self.dec_conv1 = nn.ConvTranspose2d(32, 16, 3, stride=2, padding=1, output_padding=1)
        self.dec_conv2 = nn.ConvTranspose2d(16, 1, 3, stride=2, padding=1, output_padding=1)

    def encode(self, x):
        h = F.relu(self.enc_conv1(x))
        h = F.relu(self.enc_conv2(h))
        h = h.view(-1, 32 * 7 * 7)
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        h = self.fc_decode(z)
        h = h.view(-1, 32, 7, 7)
        h = F.relu(self.dec_conv1(h))
        h = torch.sigmoid(self.dec_conv2(h))
        return h

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar
