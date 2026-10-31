from __future__ import annotations

import torch

from residuum.steering import ResidualSteer, last_token_hidden, mean_difference


def test_mean_difference_unit_and_direction() -> None:
    pos = torch.tensor([[2.0, 0.0], [4.0, 0.0]])
    neg = torch.tensor([[0.0, 2.0], [0.0, 4.0]])
    v = mean_difference(pos, neg)
    assert v.shape == (2,)
    assert torch.allclose(torch.linalg.vector_norm(v), torch.tensor(1.0), atol=1e-5)
    # pos mean is (3,0), neg mean is (0,3), difference (3,-3) -> toward +x, -y
    assert v[0] > 0
    assert v[1] < 0


def test_mean_difference_zero() -> None:
    x = torch.ones(4, 8)
    v = mean_difference(x, x)
    assert torch.count_nonzero(v).item() == 0


def test_last_token_hidden() -> None:
    h = torch.arange(24, dtype=torch.float32).view(2, 3, 4)
    last = last_token_hidden(h)
    assert torch.equal(last[0], h[0, -1])
    assert torch.equal(last[1], h[1, -1])


class _Layer(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear = torch.nn.Linear(4, 4, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x)


def test_residual_steer_includes_last_prompt_token() -> None:
    layer = _Layer()
    with torch.no_grad():
        layer.linear.weight.copy_(torch.eye(4))
    vec = torch.tensor([1.0, 0.0, 0.0, 0.0])
    steer = ResidualSteer(vec, prompt_len=2, coeff=1.0)
    steer.attach(layer)
    x = torch.ones(1, 5, 4)
    y = layer(x)
    steer.remove()
    # identity keeps ones; rms=1 so we add 1 * vec at last prompt token onward
    assert torch.allclose(y[0, 0], torch.ones(4))
    assert torch.allclose(y[0, 1], torch.ones(4) + vec)
    assert torch.allclose(y[0, 4], torch.ones(4) + vec)


def test_residual_steer_decode_step() -> None:
    layer = _Layer()
    with torch.no_grad():
        layer.linear.weight.copy_(torch.eye(4))
    vec = torch.tensor([0.0, 1.0, 0.0, 0.0])
    steer = ResidualSteer(vec, prompt_len=10, coeff=2.0)
    steer.attach(layer)
    x = torch.ones(1, 1, 4)
    y = layer(x)
    steer.remove()
    # rms=1, coeff=2 -> add 2 * vec
    assert torch.allclose(y[0, 0], torch.ones(4) + 2 * vec)
