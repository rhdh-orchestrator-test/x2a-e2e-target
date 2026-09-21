# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible playbooks for compliance automation. **No actual migration is required** as the repository already contains Ansible playbooks and serves as educational/demonstration content rather than production infrastructure code.

## Module Migration Plan

This repository contains demonstration examples rather than production modules requiring migration:

### MODULE INVENTORY

**No Chef cookbooks or recipes found for migration.** This repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates and basic virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already target technology)
    - Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, service management

- **poodle_fix**:
    - Description: Ansible playbook demonstrating SSL protocol hardening by disabling SSLv3 and enforcing TLSv1.2 only
    - Path: chef-and-ansible/poodle_fix.yml  
    - Technology: Ansible (already target technology)
    - Key Features: Apache SSL configuration remediation, POODLE vulnerability mitigation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality and SSL protocol configuration
- `tests/ssh_profile.rb`: InSpec compliance profile testing SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)
- **Cloud Platform**: Not specified (local development environment)

## Migration Approach

### Key Dependencies to Address

**No external dependencies requiring migration** - the existing Ansible playbooks use standard modules:
- **apache2 (2.4.41-4ubuntu3.10)**: Already managed via Ansible apt module
- **openssl/python3-openssl**: Certificate management handled by Ansible openssl_* modules
- **curl**: Standard package installation via apt module

### Security Considerations

**Existing security practices already implemented in Ansible:**
- SSL/TLS certificate management: Self-signed certificates generated via Ansible openssl modules
- Protocol hardening: TLSv1.2 enforcement, SSLv3 disabled
- SSH security: InSpec tests verify PermitRootLogin restrictions
- File permissions: Proper mode settings (0640 for certs, 0755 for directories, 0644 for web content)

**Vault/secrets management**: 
- No encrypted data bags or Chef Vault usage detected
- Hardcoded credentials present in deployment scripts (userpassword='password') - should be externalized to Ansible Vault
- SSL certificates are self-signed and generated dynamically - no pre-existing certificate management

### Technical Challenges

**No significant technical challenges** as content is already in Ansible format:
- **InSpec Integration**: Current setup uses Test Kitchen with InSpec verifier - can be maintained or migrated to Ansible Molecule with InSpec
- **Compliance Testing**: InSpec profiles provide STIG compliance verification - consider integrating with Ansible compliance collections
- **Chef Infrastructure Dependencies**: Deployment scripts install Chef Automate/Server - evaluate if these are still needed in pure Ansible environment

### Migration Order

**No migration required** - repository serves as reference implementation:
1. **Evaluate InSpec Integration**: Determine if Chef InSpec should be replaced with Ansible compliance scanning or maintained as-is
2. **Security Hardening**: Move hardcoded credentials from deployment scripts to Ansible Vault
3. **Documentation Update**: Update README to clarify the repository's purpose as Ansible + InSpec examples

### Assumptions

- Repository serves as educational/demonstration content rather than production infrastructure
- Chef InSpec integration is intentional for compliance automation workflows
- Deployment scripts are for lab/development environments only (evidenced by hardcoded credentials)
- No actual Chef cookbooks exist that require migration to Ansible
- Ubuntu 20.04 target environment is appropriate for demonstration purposes
- Self-signed certificates are acceptable for testing/demo scenarios
- Test Kitchen + InSpec workflow is preferred over Ansible Molecule for this use case