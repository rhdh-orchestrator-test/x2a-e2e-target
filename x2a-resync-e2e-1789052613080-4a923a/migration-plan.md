# MIGRATION FROM MIXED ANSIBLE/CHEF INSPEC TO ANSIBLE

This repository is a demonstration/example repository that showcases using Chef InSpec alongside Ansible for compliance automation. It contains existing Ansible playbooks with Chef InSpec testing, rather than traditional Chef cookbooks requiring migration. The primary migration need is to replace Chef InSpec tests with native Ansible testing approaches and consolidate the Chef server deployment scripts into Ansible automation.

## Module Migration Plan

This repository contains mixed technologies that need consolidation rather than traditional migration:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server with HTTPS configuration, self-signed SSL certificates, and virtual host setup for a simple "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, package management for Ubuntu 20.04

**ssl-security-hardening**:
- Description: SSL/TLS security hardening for Apache to disable vulnerable protocols (POODLE fix)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: SSL protocol restriction to TLS 1.2 only, Apache configuration modification

**chef-server-deployment**:
- Description: Automated deployment scripts for Chef Automate and Chef Infra Server infrastructure
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate installation, user and organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration using Vagrant driver with Ansible provisioner and InSpec verifier
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test file for web server validation
- `deploy-automate.sh`: Chef Automate and Infra Server deployment automation
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment automation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbooks)
- **Virtual Machine Technology**: Vagrant with VirtualBox (based on Test Kitchen configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible native testing using `ansible.builtin.uri`, `ansible.builtin.service_facts`, and `ansible.builtin.assert` modules
- **Test Kitchen**: Replace with Molecule for Ansible testing framework
- **Chef Automate/Server**: Consolidate deployment scripts into Ansible playbooks with proper idempotency

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates - consider integration with Let's Encrypt or proper CA management
- **Hardcoded Credentials**: The Chef server deployment scripts contain hardcoded passwords and user credentials that need to be externalized to Ansible Vault
- **SSH Security Testing**: The InSpec SSH compliance test needs conversion to Ansible native validation
- **STIG Compliance**: Maintain existing security compliance checks (SSH root login disabled, SSL protocol restrictions) in Ansible format

### Technical Challenges

- **InSpec to Ansible Test Conversion**: Converting Chef InSpec compliance tests to native Ansible assertions while maintaining the same security validation coverage
- **Test Kitchen Replacement**: Migrating from Test Kitchen/InSpec workflow to Molecule/Ansible native testing
- **Chef Server Dependencies**: The deployment scripts assume Chef infrastructure - need to determine if Chef server deployment is still required or can be eliminated
- **Compliance Framework**: Maintaining STIG compliance validation (currently handled by InSpec) using Ansible native approaches

### Migration Order

1. **SSL Security Hardening** (already complete - no migration needed)
2. **Apache HTTPS Website** (already complete - no migration needed)  
3. **Test Framework Migration** (convert InSpec tests to Ansible native testing)
4. **Chef Server Deployment** (convert bash scripts to Ansible playbooks)
5. **Compliance Integration** (establish new testing workflow without Chef InSpec dependency)

### Assumptions

- The repository serves as a demonstration/example rather than production infrastructure code
- Chef InSpec testing capability needs to be preserved but implemented through Ansible native approaches
- Chef server deployment automation may still be required for organizations using Chef alongside Ansible
- Ubuntu 20.04 target environment will be maintained (though playbooks should be updated for newer Ubuntu versions)
- Test Kitchen workflow needs replacement with Molecule for consistent Ansible testing
- Security compliance requirements (STIG) must be maintained through the migration process
- The existing Ansible playbooks are already well-structured and don't require significant refactoring
- Self-signed certificate approach is acceptable for demonstration purposes but should be enhanced for production use