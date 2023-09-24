# Spain bot

App for users to get information about the visa center BLS-Spain.

## Getting Started

This project is a starting point for a Flutter application.

### Features available

- [x] Get started with the bot.
- [x] Send a cookie to the bot.
- [x] Listening to changes if some new appointment is available.
- [x] Get a direct link to the appointment page (first you need to paste the actual cookie from the bot to the browser).

### Features to be implemented

- [ ] Get an actual cookie from the browser page without opening DevTools.
- [ ] Get a direct link to the appointment page with filled data from the bot.

### Requirements

- [Firebase Admin SDK](https://firebase.google.com/docs/reference/admin/python)
- [Firebase Functions](https://firebase.google.com/docs/functions/get-started?gen=2nd#python-preview)
- [Python telegram bot](https://pypi.org/project/pyTelegramBotAPI/#getting-started)

### How to run the project

1. Create a new project in Firebase.
2. You need to have a paid plan to use Cloud Functions.
3. Enable Cloud Firestore, Cloud Functions (Python as in the example).
4. Create a new bot in Telegram.
5. Run `firebase init` in the project folder.
6. Add the bot token to the `key.py` file in the `const` folder.
7. Run `firebase deploy --only functions` to deploy the bot to the Firebase.
8. Run `firebase serve` to start the bot locally.
