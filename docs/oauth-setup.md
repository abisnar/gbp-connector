# One-time OAuth setup

The connector needs three secrets — `GBP_CLIENT_ID`, `GBP_CLIENT_SECRET`,
`GBP_REFRESH_TOKEN` — that you obtain once from a Google Cloud project. After
that the library handles access-token refresh on its own.

## 1. Enable the Business Profile APIs

In [Google Cloud Console](https://console.cloud.google.com/):

1. Create (or select) a project.
2. **APIs & Services → Library** → enable both:
   - *My Business Account Management API*
   - *My Business Business Information API*
3. Request production access via the
   [Business Profile APIs form](https://developers.google.com/my-business/content/prereqs).
   This is a separate gate from enabling the APIs; without it you can only
   call them as the project's owner account.

## 2. Create an OAuth client

1. **APIs & Services → Credentials → Create credentials → OAuth client ID**.
2. Application type: **Desktop** (simplest for a server-side refresh-token flow).
3. Copy the **Client ID** and **Client secret** — these become
   `GBP_CLIENT_ID` and `GBP_CLIENT_SECRET`.

## 3. Get a refresh token (one-time)

Run [Google's OAuth Playground](https://developers.google.com/oauthplayground):

1. Click the gear icon → check **Use your own OAuth credentials** → paste the
   client ID and secret from step 2.
2. In the left scope list, add
   `https://www.googleapis.com/auth/business.manage`.
3. Click **Authorize APIs**, sign in as the user who manages the business.
4. Click **Exchange authorization code for tokens**.
5. Copy the **Refresh token** — this is `GBP_REFRESH_TOKEN`. It does not expire
   unless revoked.

## 4. Put the values where the connector can find them

For local development:

```bash
cp .env.example .env
# fill in the three values
```

Then load them however you normally do (`direnv`, `python-dotenv`, your shell
profile, etc.).

For deployment:

- **GitHub Actions** — add as repository secrets, then expose them as `env:`
  on the job that runs the connector.
- **Cloud Run / Lambda / Fly.io** — set them as platform-managed secrets and
  surface them to the process as environment variables.

Never commit the real values. `.gitignore` already blocks `.env`,
`credentials.json`, `token.json`, and service-account JSON; the CI
`secret-scan` job runs `gitleaks` on every push as a backstop.
