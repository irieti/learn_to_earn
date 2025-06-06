🧠 LearnEarn — AI-powered Learn-to-Earn Platform on Rootstock

LearnEarn is a gamified Learn-to-Earn platform powered by AI and integrated with Rootstock.
Users complete personalized Web3 learning tasks and earn rewards such as internal tokens, NFTs, and optionally RIF from partner-sponsored quests.

🚀 Platform Overview

🎓 For learners:
Learn core Web3 topics (DeFi, wallets, privacy, contracts, etc.)
Complete tasks generated by an AI agent and track your progress
Earn internal tokens, NFT badges, and possibly RIF (if offered by the sponsoring project)
Level up your profile and unlock new missions

🤝 For Web3 projects:
Launch custom learning quests for users with token/NFT rewards
Provide RIF or other incentives for completed actions (e.g., on-chain transactions)
Use the platform as an onboarding and education tool for your protocol
Let our AI agent build tasks tailored to different user levels automatically

🧠 AI Agent Features

The built-in AI agent:

Creates learning paths based on user experience and skills
Verifies task completion (e.g., checks on-chain transactions via tx_hash)
Issues rewards like NFTs or internal tokens
Provides feedback and motivational progress tracking

⚙️ Olas Integration
Integration to Olas network for AI-agents communication to make new quizes

Pushed to IPFS, but due to docker technical issues couldnt finish this part
\*\* Pushed component with:
PublicId: irieti/learn_earn_web3_agent:0.1.0
Package hash: bafybeifdrkspjqhe5zuolwwnztc7e3qo65nnzawvzgy4zksy4elnxsor6m
Pushed component with:
PublicId: irieti/learn_earn_web3_agent:0.1.0
Package hash: bafybeifsz3q2a4q2mpzt4lzq3cwsutk73bdfclpijn2atghi66hs2tivma

⚙️ Rootstock Integration

✅ Deployed on Rootstock — smart contracts for task verification and reward issuance
✅ NFT badge minting occurs on Rootstock
✅ Quests by projects can offer RIF as an incentive (optional, if project sponsors it)

🧪 Example: Rewarding Users

After verifying a successful transaction, the platform may call:

issue_token_reward("0xUserWallet", 3.5) # sends 3.5 internal tokens
To mint an NFT badge for a completed quest:

mint_nft_badge("0xUserWallet", {"id": "quest-xyz"})

📦 Tech Stack

Python, Web3.py, Django
Smart contract interaction on Rootstock
AI-driven task creation and validation
Optional RIF-based incentive system via project partnerships
