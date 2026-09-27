# MIGRATION FROM CHEF TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec compliance testing, representing a hybrid approach that combines Ansible for configuration management with Chef InSpec for compliance verification.

**Migration Status**: No traditional migration required - this is an example repository showing Chef InSpec + Ansible integration patterns.

## Module Migration Plan

This repository contains demonstration code and deployment scripts rather than production Chef cookbooks:

### MODULE INVENTORY

**No Chef cookbooks found for migration.** This repository contains:

- **website-https-demo**:
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates and SSL hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4 installation, SSL certificate generation, virtual host configuration, security hardening

- **poodle-ssl-fix**:
    - Description: Ansible playbook for SSL protocol hardening to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: SSL protocol restriction to TLS 1.2, Apache configuration updates

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL configuration
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security hardening verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server verification

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

**No Chef cookbook dependencies to migrate.** Current dependencies:
- **Apache 2.4.41**: Already configured via Ansible apt module
- **OpenSSL/PyOpenSSL**: Certificate management handled by Ansible openssl modules
- **Chef InSpec**: Compliance testing framework (retain for continuous compliance)

### Security Considerations

- **SSL/TLS Configuration**: Playbooks demonstrate proper SSL hardening practices
  - Self-signed certificate generation for development/testing
  - SSL protocol restriction to TLS 1.2 only
  - Proper certificate file permissions (0640)
- **SSH Hardening**: InSpec profile validates SSH root login restrictions
- **No hardcoded credentials**: Configuration uses variables and generated certificates
- **Compliance Testing**: InSpec profiles provide continuous security validation

### Technical Challenges

**No migration challenges - content is already Ansible-based.** Considerations for adoption:

- **Test Kitchen Integration**: Current setup uses Test Kitchen with Ansible provisioner and InSpec verifier
- **InSpec Profile Management**: SSH security profile demonstrates compliance-as-code patterns
- **Certificate Management**: Self-signed certificates suitable for testing but production requires CA-signed certificates
- **Service Handler Coordination**: Playbooks show proper handler usage for service restarts

### Migration Order

**No migration required.** For teams adopting this pattern:

1. **Infrastructure Setup** (setup-automate scripts) - Deploy Chef Automate for InSpec profile management
2. **Ansible Playbook Deployment** (website_https.yml) - Core configuration management
3. **Security Hardening** (poodle_fix.yml) - SSL protocol restrictions
4. **Compliance Validation** (InSpec profiles) - Continuous compliance verification

### Assumptions

- This repository serves as a reference implementation rather than production infrastructure requiring migration
- Teams using this pattern will maintain Chef InSpec for compliance testing while using Ansible for configuration management
- The hybrid approach (Ansible + InSpec) is intentional and represents the target architecture
- Production deployments will require CA-signed certificates rather than self-signed certificates
- Chef Automate deployment scripts assume sufficient system resources (vm.max_map_count, memory requirements)
- Test Kitchen configuration assumes Vagrant availability for local testing environments
- InSpec profiles may need customization for specific organizational compliance requirements