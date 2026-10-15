# MIGRATION FROM CHEF TO ANSIBLE

This migration plan outlines the process to convert Chef cookbooks to Ansible roles. The repository contains 3 Chef cookbooks that are primarily test fixtures for credential handling, default values, and type management. These cookbooks are small in scope but represent important patterns that need careful consideration during migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-flpath-4648-credentials**:
    - Description: Chef cookbook demonstrating credential handling with required API tokens that don't have default values
    - Path: fixtures/chef-flpath-4648-credentials
    - Technology: Chef
    - Key Features: Credential management, templated configuration with sensitive data, file permissions (0600)

- **chef-flpath-4648-no-defaults**:
    - Description: Chef cookbook representing an edge case where no default attributes are defined
    - Path: fixtures/chef-flpath-4648-no-defaults
    - Technology: Chef
    - Key Features: Simple file creation without attribute dependencies

- **flpath-4648-types**:
    - Description: Chef cookbook demonstrating various data types (scalar, collection, nested) in attribute definitions
    - Path: fixtures/chef-flpath-4648-types
    - Technology: Chef
    - Key Features: Directory creation, configuration file generation, complex data structures

### Infrastructure Files

- `x2a-rules/a01cd631-c343-4fc5-8ed0-05b211db7ad4.md`: Rule file specifying that Ansible output must include a specific marker. This suggests integration with a testing framework or validation system.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: The chef-flpath-4648-types cookbook explicitly supports Ubuntu 18.04+ and CentOS 7.0+, suggesting these are the target OSes.
- **Virtual Machine Technology**: Not specified in the available files.
- **Cloud Platform**: Not specified in the available files.

## Migration Approach

### Key Dependencies to Address
- **Chef (v17.0+)**: Replace with Ansible core modules and standard YAML structure
- **Chef Attributes**: Convert to Ansible variables with appropriate defaults in `defaults/main.yml`

### Security Considerations
- **API Token Handling**: The chef-flpath-4648-credentials cookbook explicitly handles an API token as a sensitive attribute without a default. This pattern should be migrated to Ansible Vault or AAP Credentials.
- **File Permissions**: The credentials configuration file is set with 0600 permissions. Maintain these strict permissions in the Ansible equivalent.
- **Vault/secrets management**: For each module, identify credential patterns:
  - chef-flpath-4648-credentials: Contains sensitive API token that must be handled securely
  - No hardcoded credentials were found in the reviewed files
  - Files with sensitive content are properly secured with restricted permissions

### Technical Challenges
- **Data Type Preservation**: Ensuring that boolean, numeric, string, and collection types are correctly preserved during migration, especially for the flpath-4648-types cookbook
- **Credential Management**: Implementing a secure credential injection mechanism similar to what's expected in the chef-flpath-4648-credentials cookbook
- **Rule Compliance**: Ensuring the generated Ansible code includes the required marker "FLPATH-3351-TC-07-RULE" as specified in the rule file

### Migration Order
1. chef-flpath-4648-no-defaults (lowest complexity, no attribute dependencies)
2. flpath-4648-types (medium complexity, various data types but no security concerns)
3. chef-flpath-4648-credentials (highest complexity due to security considerations)

### Assumptions
1. These cookbooks appear to be test fixtures rather than production code, designed to test a Chef-to-Ansible migration tool's handling of various patterns.
2. The rule file suggests there may be automated testing or validation of the migrated Ansible code.
3. The mention of "AAP-injected credential" in comments suggests the target environment may include Ansible Automation Platform.
4. The repository structure is incomplete - there may be additional files or dependencies not visible in the current directory listing.
5. There's no clear indication of orchestration or run order between these cookbooks.
6. No external cookbook dependencies were declared in the metadata files.