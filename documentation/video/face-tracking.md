# Face tracking

Detected boxes are assigned to tracks by intersection-over-union and a bounded temporal gap. Track identifiers are local to one video job. Occlusion, cuts, very small faces, and similar overlapping faces can split or merge identities; track IDs are not biometric identities.
