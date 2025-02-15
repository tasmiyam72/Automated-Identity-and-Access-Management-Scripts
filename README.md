# Automated Identity and Access Management Scripts

## Overview

Managing user access, application registrations, and security configurations across multiple platforms like Azure AD, Okta, and HashiCorp Vault can be complex and time-consuming. This repository provides powerful automation scripts written in Python to simplify these tasks, ensuring security, efficiency, and scalability in identity and access management (IAM).

Each script automates a specific IAM process, reducing manual effort, improving consistency, and enhancing compliance across enterprise environments. Whether you're managing bulk user removals, app registrations, or MFA key generation, these scripts will help streamline operations.

## Available Scripts

1️⃣ _**Bulk Application Registration Deletion (Azure AD)**__

🔹 Purpose: Automates the process of removing multiple application registrations from Azure AD in one go.

🔹 **Key Features:**

Uses Microsoft Graph API for secure deletion.

Processes a list of application registrations efficiently.

Reduces manual workload and ensures compliance with security policies.

🔹 **How It Works:**

Reads a list of application IDs.

Authenticates with Azure AD.

Deletes all specified applications automatically.

2️⃣ _**Remove Bulk Users from Okta Tenant**__

🔹 **Purpose**: Automates bulk user removal from an Okta Tenant, reducing the need for manual intervention.

🔹 **Key Features:**

Uses Okta API for seamless user management.

Handles bulk operations efficiently to maintain directory hygiene.

Ensures compliance with IAM policies.

🔹 **How It Works:**

Reads a file containing a list of users.

Authenticates with Okta API.

Deletes users from the Okta tenant in bulk.

3️⃣_ **Remove Bulk Users from an Azure AD Group**_

🔹 **Purpose: **Removes multiple users from an Azure AD Group to maintain security and access control.

🔹 **Key Features:**

Uses Microsoft Graph API to interact with Azure AD.

Fetches user details before removing them from the group.

Handles bulk operations with efficiency and error handling.

🔹 **How It Works:**

Reads a list of users from a file.

Authenticates with Azure AD.

Removes each user from the specified group.

4️⃣ _**Vault MFA Key Generator**_

🔹 **Purpose:** Automates MFA key creation, retrieval, and deletion in HashiCorp Vault, ensuring secure authentication practices.

🔹** Key Features:**

Uses HashiCorp Vault API for secure MFA key storage.

Automates MFA key generation, listing, and cleanup.

Enhances security by managing secrets programmatically.

🔹 **How It Works:**

Authenticates with Vault.

Lists stored MFA secrets.

Processes keys and removes outdated ones as needed.

💡 ## Why Use These Scripts?

✅ Automated & Efficient: Reduces manual effort by handling bulk operations.
✅ Secure & Compliant: Uses APIs to ensure safe and authenticated execution.
✅ Scalable: Designed for enterprise-level identity and access management.
✅ Time-Saving: Eliminates repetitive tasks, freeing up IT resources.

# 🚀 Getting Started

## Prerequisites

  Python 3.8+ installed.
  
  Required dependencies installed:
  
  `pip install -r requirements.txt`
  
  Environment variables configured as needed (Vault credentials, API tokens, etc.).

## Usage

Run the respective script based on your requirements:

```python
python bulk_app_reg_delete.py  # Delete Azure AD app registrations
python remove_bulk_users_okta.py  # Remove users from Okta
python remove_bulk_users_group.py  # Remove users from an Azure AD Group
python vault_mfa_generator.py  # Generate and delete MFA keys in Vault 

## 🤝 Contributing

We welcome contributions! Feel free to open an issue or submit a pull request to improve these scripts.

## Disclaimer

🚀 Automate IAM tasks, enhance security, and save time with these Python scripts! 🔐


