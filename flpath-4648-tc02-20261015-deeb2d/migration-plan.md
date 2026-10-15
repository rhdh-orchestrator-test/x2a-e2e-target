# MIGRATION FROM CHEF TO ANSIBLE

This repository contains three Chef cookbooks that are used as test fixtures for the X2A (Chef-to-Ansible) conversion process. The cookbooks demonstrate various aspects of Chef attribute handling, particularly focusing on credential handling, default values, and type definitions. The migration scope is small but demonstrates several important patterns that will need to be handled in Ansible.

## Module Migration Plan

This repository contains 3 Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-flpath-4648-credentials**:
    - Description: Chef cookbook demonstrating credential-like variable handling with API token injection
    - Path: fixtures/chef-flpath-4648-credentials
    - Technology: Chef
    - Key Features: API credential management, file template with secure permissions (0600)

- **chef-flpath-4648-no-defaults**:
    - Description: Minimal Chef cookbook with no default attributes to test edge cases
    - Path: fixtures/chef-flpath-4648-no-defaults
    - Technology: Chef
    - Key Features: Simple file resource without attribute defaults

- **flpath-4648-types**:
    - Description: Chef cookbook demonstrating various data types including scalar, collection, and nested structures
    - Path: fixtures/chef-flpath-4648-types
    - Technology: Chef
    - Key Features: Multiple data types (strings, booleans, integers, floats, arrays, nested hashes)

### Infrastructure Files

- `x2a-rules/a01cd631-c343-4fc5-8ed0-05b211db7ad4.md`: Contains a specific rule for the migration process, requiring inclusion of a marker in the Ansible output.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ based on metadata in flpath-4648-types cookbook
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address
- **Chef (>= 17.0)**: Replace with Ansible Core. The cookbooks require a modern Chef version but don't use any complex Chef-specific features that would require specialized Ansible modules.

### Security Considerations
- **API Token Handling**: The chef-flpath-4648-credentials cookbook demonstrates a pattern for handling sensitive API tokens:
  - Migration approach: Use Ansible Vault or AAP Credentials for the api_token variable
  - File permissions: Ensure the 0600 permissions are preserved in the Ansible file module
- **Credential Storage**: 
  - The cookbooks demonstrate pattern of not storing sensitive data in defaults
  - Credential references need to be replaced with Ansible Vault or AAP Credential type

### Technical Challenges
- **Data Type Preservation**: The flpath-4648-types cookbook uses various data types (strings, booleans, integers, floats, arrays, nested hashes) that must be preserved in the Ansible variables.
  - Mitigation: Use YAML typing in Ansible variables, ensuring nested structures are properly preserved
- **Default Values Logic**: Chef's attribute precedence differs from Ansible's variable precedence
  - Mitigation: Review all defaults and ensure they are properly mapped to Ansible's variable precedence system
- **X2A Rules Integration**: The repository contains custom rules for the migration process
  - Mitigation: Ensure that the Ansible playbooks comply with the rules specified in the x2a-rules directory, specifically including the "FLPATH-3351-TC-07-RULE" marker

### Migration Order
1. chef-flpath-4648-no-defaults (lowest complexity, no attributes to migrate)
2. chef-flpath-4648-credentials (medium complexity, security considerations)
3. flpath-4648-types (highest complexity due to various data types)

### Assumptions
- The cookbooks appear to be test fixtures rather than production code, but the patterns they demonstrate are likely relevant to real-world Chef-to-Ansible migrations
- The x2a-rules directory suggests this is part of a larger migration framework with specific requirements
- No complex Chef-specific features (like search, data bags, etc.) are being used in these cookbooks
- The target environment supports both Ubuntu and CentOS as specified in the metadata
- The cookbooks are focused on testing attribute conversion patterns rather than implementing complex infrastructure