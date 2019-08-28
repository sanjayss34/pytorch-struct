import torch
from .semirings import LogSemiring
from .helpers import _make_chart

def linearchain_inside(edge, semiring=LogSemiring):
    """
    Parameters:
         edge : b x N x C x C semimarkov potentials
         semiring

    Returns:
         v: b tensor of total sum
         alpha: list of N,  b x C table

    """
    batch, N, C, _ = edge.shape
    alpha = [_make_chart((batch, C), edge, semiring)
             for n in range(N+1)]
    alpha[0].data.fill_(semiring.one())
    for n in range(1, N + 1):
        alpha[n] = semiring.dot(alpha[n-1].view(batch, 1, C),
                                edge[:, n-1])
    return semiring.sum(alpha[N]), alpha


def linearchain(edge, semiring=LogSemiring):
    """
    Parameters:
         edge : b x N x C x C semimarkov potentials
         semiring

    Returns:
         marginals: list of N,  b x C table

    """
    v, alpha = linearchain_inside(edge, semiring)
    return torch.autograd.grad(v.sum(dim=0), alpha, create_graph=True,
                               only_inputs=True, allow_unused=False)


### Tests

def linearchain_check(edge, semiring=LogSemiring):
    batch, N, C, _ = edge.shape
    chains = [([c], torch.zeros(batch).fill_(semiring.one()))
              for c in range(C)]
    for n in range(1, N + 1):
        new_chains = []
        for chain, score in chains:
            for c in range(C):
                new_chains.append((chain + [c],
                                   semiring.mul(score,
                                                edge[:, n-1, c, chain[-1]])))
        chains =new_chains

    return semiring.sum(torch.stack([s for (_, s) in chains]), dim=0)
