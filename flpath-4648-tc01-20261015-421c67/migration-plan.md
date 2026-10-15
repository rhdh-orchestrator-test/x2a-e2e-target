# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This migration plan addresses the conversion of a small Chef cookbook repository to Ansible. The repository contains three Chef cookbooks that appear to be test fixtures for a tool called "x2a" (likely a Chef-to-Ansible conversion tool). The cookbooks demonstrate different patterns for handling credentials, default values, and variable types.

Given the small scope (3 simple cookbooks) and test-oriented nature of this repository, the migration complexity is **LOW**. Estimated timeline for migration: **1-2 days** for a complete conversion of all cookbooks to equivalent Ansible roles.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-flpath-4648-credentials**:
    - Description: Test fixture for handling credential-like variables, specifically demonstrating required parameters without defaults (like API tokens) that would be injected by Ansible Automation Platform
    - Path: fixtures/chef-flpath-4648-credentials
    - Technology: Chef
    - Key Features: Credential handling pattern, secure file permissions (0600), attribute pattern for API endpoint configuration

- **chef-flpath-4648-no-defaults**:
    - Description: Test fixture demonstrating a cookbook with no default attributes defined, representing an edge case for migration
    - Path: fixtures/chef-flpath-4648-no-defaults
    - Technology: Chef
    - Key Features: Simple file creation with no variable substitution, standard file permissions (0644)

- **chef-flpath-4648-types**:
    - Description: Test fixture demonstrating various data types and nested values in Chef attributes
    - Path: fixtures/chef-flpath-4648-types
    - Technology: Chef
    - Key Features: Boolean, integer, float, array, and hash data types; dynamic file paths based on attributes; iteration through nested hash structures; directory creation

### Infrastructure Files

- `x2a-rules/a01cd631-c343-4fc5-8ed0-05b211db7ad4.md`: Test marker rule for x2a conversion tool, specifies that generated Ansible code must include a specific marker (FLPATH-3351-TC-07-RULE)

### Target Details

Based on the source configuration files:

- **Operating System**: Linux (implied by file paths like '/etc/' and Unix-style file permissions)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified (example.test domains suggest this is for testing environments only)

## Migration Approach

### Key Dependencies to Address
- **Chef (>= 17.0)**: Replace with Ansible core functionality
  - Chef attributes → Ansible variables
  - Chef recipes → Ansible tasks
  - Chef templates → Ansible templates
  - Chef file resources → Ansible file modules

### Security Considerations
- **Credential handling**: The chef-flpath-4648-credentials cookbook demonstrates a pattern for handling API tokens without storing defaults. In Ansible, this should be implemented using:
  - Ansible Vault for secure storage
  - AAP Credential management for production environments
  - Variable prompting or extra-vars for manual runs
- **File permissions**: Maintain the same permission model in Ansible:
  - Configuration with credentials: 0600
  - Standard configuration: 0644

### Technical Challenges
- **Data type preservation**: Ensure proper handling of boolean, numeric, and complex data structures when converting Chef attributes to Ansible variables
- **Nested variable structures**: Maintain the hierarchical structure of nested hashes/dictionaries during conversion
- **Dynamic file paths**: Properly handle the interpolation of variables in file paths

### Migration Order
1. chef-flpath-4648-no-defaults (simplest cookbook, good starting point)
2. chef-flpath-4648-types (more complex with various data types)
3. chef-flpath-4648-credentials (requires special handling for credentials)

### Assumptions
- The repository appears to be a test fixture for an automated conversion tool (x2a) rather than production infrastructure code
- The cookbooks are intentionally simple to test specific conversion patterns
- The mention of "AAP-injected credential" suggests the target environment will be Ansible Automation Platform
- The x2a-rules file suggests this is part of a testing framework for validating Chef to Ansible conversion logic