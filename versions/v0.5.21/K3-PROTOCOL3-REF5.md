# Kimi protocol3-ref5 focused native repair

The complete engine source is `9d263bb062181b040edf85877607b2fc4e6cd9f3`, retaining the exact ref4 product Python subtree `05ca454376faaeae5eba3b4d36385fd7c27d086a`. The new recipe derives from the immutable ref4 image and installs only the fixed XGrammar p6 wheel, without dependency resolution or native rebuilding.

Native source: `d645e9d0dbaf6cc85c2ca27acc8f9b4a4b83cbdc`, tree `908cc3af608ca4072717aece838d64273482b51e`; version `0.2.6rc2+phala.feedback.20261017.p6`; wheel SHA256 `ee7d54fb8b77e712e8d5e8b9f7aee59f4ead18409d6f00a4c0fb5e63ca5b7832`. The source record and deterministic p5-to-p6 delta are in `docker/phala/kimi-protocol3-ref5/` of that complete engine commit. P6 changes serialized-cache identity to `v21-phala-unordered-constraints-v3`; old p5 compiled masks must be rejected and recompiled from original grammar.

The 30-patch ref4 prefix is unchanged. One new engine patch records the recipe, native input/delta, seven frozen critical fixtures and the [public ref4 regression notice](https://github.com/Phala-Network/sglang/blob/9d263bb062181b040edf85877607b2fc4e6cd9f3/docker/phala/kimi-protocol3-ref5/RISK-REF4-943.md). All 31 ordered patches replay to the exact new engine tree. This source verification does not qualify native dynamics, the final installed image or production.
