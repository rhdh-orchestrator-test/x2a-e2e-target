# MIGRATION FROM CHEF INSPEC + ANSIBLE TO PURE ANSIBLE

This repository is a demonstration project showing Chef InSpec integration with Ansible for compliance automation. The migration scope is limited as the repository already contains Ansible playbooks with Chef InSpec used only for testing and compliance verification. The migration involves replacing Chef InSpec tests with native Ansible testing approaches and removing Chef-specific tooling dependencies.

## Module Migration Plan

This repository contains demonstration Ansible playbooks with Chef InSpec compliance tests that need migration to pure Ansible testing approaches:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host management for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, document root setup, SSL module activation

**ssl-security-hardening**:
- Description: Apache SSL protocol hardening to disable vulnerable SSL protocols and enforce TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: POODLE vulnerability mitigation, SSL protocol configuration, Apache service management

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `chef-and-ansible/index.html`: Static HTML test file for web server validation
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance test for SSH root login security configuration
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox provider (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible native testing modules (uri, assert, service, etc.)
- **Test Kitchen**: Replace with molecule for Ansible testing framework
- **Chef Automate/Server**: Remove deployment scripts as they're not needed for pure Ansible workflow
- **Vagrant Driver**: Maintain for local testing or migrate to Docker/Podman for containerized testing

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates generated via Ansible OpenSSL modules - this approach can be maintained
- **SSH Hardening Validation**: InSpec SSH root login test needs conversion to Ansible assert module or custom validation task
- **SSL Protocol Enforcement**: POODLE fix implementation is already in Ansible - compliance validation needs migration from InSpec to Ansible
- **Vault/secrets management**: No encrypted secrets detected - hardcoded test credentials in deployment scripts should be parameterized

### Technical Challenges

- **InSpec Test Conversion**: Converting Ruby-based InSpec tests to Ansible native validation requires rewriting test logic using Ansible modules (uri, assert, service, command with register/when)
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test scenarios and updating CI/CD pipelines
- **Compliance Reporting**: InSpec provides structured compliance reporting - need to implement equivalent reporting mechanism using Ansible callback plugins or custom modules
- **SSL Protocol Testing**: InSpec ssl() resource provides detailed SSL/TLS protocol testing - requires custom Ansible tasks using openssl command or uri module with SSL verification

### Migration Order

1. **apache-https-website** (low risk, already Ansible) - Convert InSpec tests to Ansible validation tasks
2. **ssl-security-hardening** (low risk, already Ansible) - Convert SSL protocol compliance tests to Ansible assertions
3. **Test Infrastructure Migration** (moderate complexity) - Replace Test Kitchen with Molecule framework
4. **Cleanup** (low risk) - Remove Chef-specific deployment scripts and dependencies

### Assumptions

- The target environment will continue using Ubuntu 20.04 LTS as specified in the current Test Kitchen configuration
- Local development and testing workflow using Vagrant will be maintained, though migration to containerized testing with Molecule is recommended
- The demonstration nature of this repository means production-grade secret management and certificate handling are not primary concerns
- SSL certificate generation will remain self-signed for demonstration purposes rather than implementing proper CA or Let's Encrypt integration
- The compliance testing requirements currently met by InSpec can be adequately replaced with Ansible native testing capabilities
- No integration with external Chef infrastructure (Chef Server, Automate) is required in the target state
- The repository will maintain its educational/demonstration purpose rather than becoming a production-ready Ansible collection
- Current Apache version pinning (2.4.41-4ubuntu3.10) may need updating for security patches during migration
- SSH hardening compliance requirements are limited to root login prevention as currently tested
- Test execution environment will support Python 3 and required Ansible dependencies (python3-openssl, etc.)