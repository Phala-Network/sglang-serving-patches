# Superseded proposals: 2026-09-20

The repository moved from independent profiles/patch exports to generated exports
from the complete engine source in `Phala-Network/sglang`. These proposals are
closed without merging. Lightweight archive tags preserve their exact branch
heads, all files and reachable history. Tags do not imply release acceptance.

| PR | Original branch | Preserved commit | Archive tag |
| --- | --- | --- | --- |
| [#1](https://github.com/Phala-Network/sglang-serving-patches/pull/1) | `codex/source-backed-v0520` | `9b6580d5ae5c83b414181a8a80e781acd94b8c7d` | `archive/2026-09-20/source-backed-v0520` |
| [#2](https://github.com/Phala-Network/sglang-serving-patches/pull/2) | `codex/glm53-v0520-profiles` | `bc9a8db40abb18ffcbe4f00065d2c917382b4e75` | `archive/2026-09-20/glm53-v0520-profiles` |
| [#3](https://github.com/Phala-Network/sglang-serving-patches/pull/3) | `codex/five-cvm-v0519-20260920` | `083fe0f9728b05a68481ecace7681c2315031ab2` | `archive/2026-09-20/five-cvm-v0519` |
| [#4](https://github.com/Phala-Network/sglang-serving-patches/pull/4) | `codex/kimi-k3-v0520-profile-r1` | `9964d2ce342a248b655ffa884fca646be33eb1db` | `archive/2026-09-20/kimi-k3-v0520-profile-r1` |
| [#5](https://github.com/Phala-Network/sglang-serving-patches/pull/5) | `codex/dsv41-v0520-profile-20260920` | `454b2e27879858daf6693a6dd0d3f541eee4447b` | `archive/2026-09-20/dsv41-v0520-profile` |

Before cleanup, main was `532de9bb401dbacc1490eba5c2bb2267bd3b719b`, with six
remote branches, five open PRs and no tags. Four workflows were already
`disabled_manually`: Kimi profile provenance (362463273), Verify GLM source
exports and profiles (362460902), Verify source-backed patch export (362469101)
and Verify v0.5.19 source exports (362462529).

The five branches were retired because they represent the superseded maintenance
process. No source proposal was force-merged or declared accepted. Archive refs
preserve unique implementation, validation and failure evidence. Existing local
worktrees and deployment inputs are outside this cleanup.

The initial documentation-only main at880cf9b was an overcorrection. The current
main restores actual ordered patches generated from complete engine4281309187;
the five historical branches remain archived because their duplicated profile
maintenance is still superseded. Restoring the current source export does not
mean merging or accepting those archived model proposals.
