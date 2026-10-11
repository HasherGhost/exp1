"""A small Deep Q-Network (DQN) agent for Merio.

This is real reinforcement learning: actions are explored, transitions are stored,
and network weights are updated using rewards from the game. No route or action
sequence is hard-coded. Uses NumPy only.
"""
from collections import deque
from pathlib import Path
import random

import numpy as np


ACTION_COUNT = 6
STATE_SIZE = 10
HIDDEN_SIZE = 32
MODEL_PATH = Path(__file__).resolve().parent / "merio_dqn.npz"


class DQNAgent:
    def __init__(self, model_path=MODEL_PATH):
        self.model_path = Path(model_path)
        self.memory = deque(maxlen=20_000)
        self.gamma = 0.97
        self.batch_size = 64
        self.learning_rate = 0.0007
        self.epsilon = 1.0
        self.epsilon_min = 0.08
        self.epsilon_decay = 0.985
        self.steps = 0
        self.episodes = 0
        self.loss = 0.0

        self.w1 = np.random.randn(STATE_SIZE, HIDDEN_SIZE).astype(np.float32) * np.sqrt(2 / STATE_SIZE)
        self.b1 = np.zeros(HIDDEN_SIZE, dtype=np.float32)
        self.w2 = np.random.randn(HIDDEN_SIZE, ACTION_COUNT).astype(np.float32) * 0.08
        self.b2 = np.zeros(ACTION_COUNT, dtype=np.float32)
        self.tw1, self.tb1, self.tw2, self.tb2 = self._copy_weights()

        # Adam state for the online network.
        self.adam_m = [np.zeros_like(w) for w in (self.w1, self.b1, self.w2, self.b2)]
        self.adam_v = [np.zeros_like(w) for w in (self.w1, self.b1, self.w2, self.b2)]
        self.adam_t = 0
        self._load()

    def _copy_weights(self):
        return tuple(w.copy() for w in (self.w1, self.b1, self.w2, self.b2))

    def _load(self):
        if not self.model_path.exists():
            return
        try:
            data = np.load(self.model_path)
            self.w1, self.b1 = data["w1"].copy(), data["b1"].copy()
            self.w2, self.b2 = data["w2"].copy(), data["b2"].copy()
            self.epsilon = float(data["epsilon"])
            self.episodes = int(data["episodes"])
            self.steps = int(data["steps"])
            self.tw1, self.tb1, self.tw2, self.tb2 = self._copy_weights()
            print(f"Loaded learned DQN model: {self.model_path.name} (episode {self.episodes})")
        except (OSError, ValueError, KeyError) as exc:
            print(f"Could not load saved DQN model ({exc}); starting fresh.")

    def save(self):
        np.savez(
            self.model_path, w1=self.w1, b1=self.b1, w2=self.w2, b2=self.b2,
            epsilon=np.float32(self.epsilon), episodes=np.int64(self.episodes),
            steps=np.int64(self.steps),
        )

    def _forward(self, states, target=False):
        if target:
            w1, b1, w2, b2 = self.tw1, self.tb1, self.tw2, self.tb2
        else:
            w1, b1, w2, b2 = self.w1, self.b1, self.w2, self.b2
        hidden_pre = states @ w1 + b1
        hidden = np.maximum(0.0, hidden_pre)
        q_values = hidden @ w2 + b2
        return q_values, hidden, hidden_pre

    def act(self, state, explore=True):
        state = np.asarray(state, dtype=np.float32).reshape(1, STATE_SIZE)
        self.steps += 1
        if explore and random.random() < self.epsilon:
            return random.randrange(ACTION_COUNT)
        q_values, _, _ = self._forward(state)
        return int(np.argmax(q_values[0]))

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((
            np.asarray(state, dtype=np.float32),
            int(action),
            float(reward),
            np.asarray(next_state, dtype=np.float32),
            bool(done),
        ))

    def train_step(self):
        if len(self.memory) < self.batch_size:
            return self.loss

        batch = random.sample(self.memory, self.batch_size)
        states = np.stack([item[0] for item in batch])
        actions = np.asarray([item[1] for item in batch], dtype=np.int64)
        rewards = np.asarray([item[2] for item in batch], dtype=np.float32)
        next_states = np.stack([item[3] for item in batch])
        dones = np.asarray([item[4] for item in batch], dtype=np.float32)

        q_values, hidden, hidden_pre = self._forward(states)
        next_q, _, _ = self._forward(next_states, target=True)
        targets = rewards + self.gamma * np.max(next_q, axis=1) * (1.0 - dones)
        errors = q_values[np.arange(self.batch_size), actions] - targets
        self.loss = float(np.mean(errors ** 2))

        grad_q = np.zeros_like(q_values)
        grad_q[np.arange(self.batch_size), actions] = (
            2.0 * np.clip(errors, -10.0, 10.0) / self.batch_size
        )
        grad_w2 = hidden.T @ grad_q
        grad_b2 = grad_q.sum(axis=0)
        grad_hidden = grad_q @ self.w2.T
        grad_hidden[hidden_pre <= 0] = 0.0
        grad_w1 = states.T @ grad_hidden
        grad_b1 = grad_hidden.sum(axis=0)

        grads = [grad_w1, grad_b1, grad_w2, grad_b2]
        params = [self.w1, self.b1, self.w2, self.b2]
        self.adam_t += 1
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        for i, (param, grad) in enumerate(zip(params, grads)):
            self.adam_m[i] = beta1 * self.adam_m[i] + (1 - beta1) * grad
            self.adam_v[i] = beta2 * self.adam_v[i] + (1 - beta2) * (grad * grad)
            m_hat = self.adam_m[i] / (1 - beta1 ** self.adam_t)
            v_hat = self.adam_v[i] / (1 - beta2 ** self.adam_t)
            param -= self.learning_rate * m_hat / (np.sqrt(v_hat) + eps)

        # Keep the target network fixed for a while to stabilize Q-learning.
        if self.steps % 500 == 0:
            self.tw1, self.tb1, self.tw2, self.tb2 = self._copy_weights()
        return self.loss

    def end_episode(self):
        self.episodes += 1
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.tw1, self.tb1, self.tw2, self.tb2 = self._copy_weights()
        self.save()
        print(
            f"DQN episode {self.episodes} | epsilon={self.epsilon:.3f} "
            f"| steps={self.steps} | replay={len(self.memory)} | loss={self.loss:.4f}"
        )

    def inspect(self, state):
        state_array = np.asarray(state, dtype=np.float32).reshape(1, STATE_SIZE)
        q_values, hidden, _ = self._forward(state_array)
        # Scale Q values only for visualization; actual values remain unchanged.
        hidden_values = np.tanh(hidden[0])
        q = q_values[0]
        q_scale = max(1.0, float(np.max(np.abs(q))))
        outputs = np.tanh(q / q_scale)
        return {
            "inputs": state_array[0].tolist(),
            "hidden": np.tanh(hidden[0][:8]).tolist(),
            "outputs": outputs.tolist(),
            "q_values": q.tolist(),
            "predicted_action": int(np.argmax(q)),
            "epsilon": self.epsilon,
            "episodes": self.episodes,
            "loss": self.loss,
        }
