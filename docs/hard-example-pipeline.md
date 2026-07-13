# Hard-example retraining handoff

DeepSight keeps model training outside this application. Reviewer corrections create a stable handoff for the training repository.

## Data flow

1. A reviewer selects **No** under an image prediction.
2. The reviewer supplies the corrected Real/Fake label. Fake corrections also include `AI-generated` or `Deepfake` and a manipulation type.
3. The backend copies the original upload into:

   `datasets/hard_examples/<category>/<manipulation>/`

4. A JSON manifest is written beside the copied media. Feedback metadata is also available from `GET /api/v1/feedback/hard-examples` and is mirrored to the Firestore `analyses_feedback` collection when Firebase is configured.

## External CI/CD integration

The training repository should periodically fetch the hard-example API or synchronize the `datasets/hard_examples` directory. Its pipeline can validate reviewer labels, deduplicate files, update the training dataset, train/evaluate a candidate model, and publish an approved checkpoint back to `backend/app/models/production`.

Do not automatically deploy a candidate checkpoint based only on training completion. Require evaluation thresholds and an approval step before replacing production weights.
