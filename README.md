# WikiBot

A Discord bot that allows users to search and read Wikipedia articles directly within Discord. Built with discord.py and the Wikipedia API.

## Features

- **Article Search**: Search Wikipedia articles with paginated results
- **Interactive Reading**: Read articles with paragraph navigation
- **Rich Content**: 
  - View article references
  - Access article images
  - Jump to specific paragraphs using dropdown menu
- **User-Friendly Interface**: 
  - Interactive buttons for navigation
  - Clean embeds for better readability
  - Error handling with clear messages

## Commands

- `/search <query>` - Search for Wikipedia articles
- `/article <title>` - Directly view a specific article
- `/ping` - Check bot latency
- `/about` - View information about the bot

## Usage

### Search Articles
1. Use `/search` followed by your query
2. Click on any result to read the article
3. Navigate through multiple results using "Previous Results" and "More Results" buttons

### Read Articles
- Use the dropdown menu to jump to specific paragraphs
- Click "Next Paragraph" to read sequentially
- View references and images using the respective buttons
- Click "Stop Reading" to end the session

## Installation

#Install official bot

1. [Invite link](https://discord.com/oauth2/authorize?client_id=1339958854238212167)

# Install bot yourself

1. Clone the repository
```bash
git clone https://github.com/DaDevMikey/WikiBot.git
```

2. Install required packages
```bash
pip install discord.py wikipedia-api
```

3. Configure the bot
   - Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
   - Get your bot token
   - Replace `'YOUR_BOT_TOKEN'` in `main.py` with your actual token

4. Run the bot
```bash
python main.py
```

## Requirements

- Python 3.8 or higher
- discord.py
- wikipedia-api
- Discord Bot Token

## Contributing

Feel free to contribute to this project by:
1. Forking the repository
2. Creating a new branch
3. Making your changes
4. Submitting a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- Website: [nexas-development.vercel.app](https://nexas-development.vercel.app)
- GitHub: [@DaDevMikey](https://github.com/DaDevMikey)

## Support

If you encounter any issues or have suggestions, please open an issue on GitHub.

## Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Wikipedia content accessed through [wikipedia-api](https://pypi.org/project/wikipedia-api/)
```

