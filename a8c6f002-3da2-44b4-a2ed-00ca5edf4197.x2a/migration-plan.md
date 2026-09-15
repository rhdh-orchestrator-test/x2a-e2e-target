# MIGRATION FROM CHEF TO ANSIBLE

This repository is a demonstration/example repository that showcases Chef InSpec integration with Ansible for compliance automation. **No traditional Chef cookbooks require migration** - the repository already contains Ansible playbooks and uses Chef InSpec purely for testing and compliance verification. The migration scope is minimal, focusing on consolidating the existing Ansible automation and potentially replacing InSpec tests with native Ansible testing approaches.

## Module Migration Plan

This repository contains demonstration content and deployment scripts rather than production Chef cookbooks:

### MODULE INVENTORY

**No Chef cookbooks found for migration.** This repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: SSL certificate generation, Apache virtual host configuration, package management

- **poodle_fix**:
    - Description: Ansible playbook demonstrating SSL protocol hardening by disabling SSLv3 and enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration hardening, POODLE vulnerability mitigation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration using Ansible provisioner and InSpec verifier for testing automation
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality, SSL protocols, and web service availability
- `tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server verification

### Target Details

Based on the existing Ansible playbooks and test configurations:

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies to migrate** - this repository uses:
- **Chef InSpec**: Currently used for compliance testing and verification - consider replacing with Ansible native testing or maintaining for compliance automation
- **Test Kitchen**: Used for testing infrastructure - can be replaced with molecule for Ansible-native testing
- **Apache 2.4.41**: Already managed via Ansible apt module with specific version pinning

### Security Considerations

The existing implementation already demonstrates good security practices:
- **SSL/TLS Configuration**: Self-signed certificate generation with proper key management, SSL protocol hardening (TLS 1.2 enforcement)
- **SSH Hardening**: InSpec tests verify SSH root login is disabled per STIG requirements
- **File Permissions**: Proper file and directory permissions (0640 for certificates, 0755 for web directories)
- **No Hardcoded Secrets**: Uses Ansible variables and generated certificates rather than embedded credentials

### Technical Challenges

**Minimal technical challenges** as this is primarily a demonstration repository:
- **Testing Strategy**: Decision needed on whether to maintain InSpec for compliance testing or migrate to Ansible native testing (ansible-test, molecule)
- **Environment Consistency**: The deployment scripts create specific user accounts and organizations that may need standardization for production use
- **SSL Certificate Management**: Current implementation uses self-signed certificates - production deployment would require CA-signed certificates or Let's Encrypt integration

### Migration Order

**No migration required** - repository is already Ansible-based. Potential improvements:

1. **Testing Framework Consolidation** (low complexity): Evaluate replacing InSpec with Ansible native testing
2. **Deployment Script Enhancement** (moderate complexity): Convert bash deployment scripts to Ansible playbooks for consistency
3. **Production Readiness** (moderate complexity): Add proper certificate management and environment-specific configurations

### Assumptions

- This repository serves as a demonstration/training resource rather than production infrastructure code
- The Chef components (InSpec, Automate, Infra Server) are intentionally maintained for compliance automation and demonstration purposes
- The existing Ansible playbooks represent the desired end state rather than legacy code requiring migration
- Test Kitchen and InSpec integration is a deliberate architectural choice for compliance automation workflows
- The Ubuntu 20.04 target platform and specific Apache version (2.4.41-4ubuntu3.10) are demonstration-specific and may need updating for production use
- The self-signed certificate approach is acceptable for demonstration but would require proper PKI integration for production deployment