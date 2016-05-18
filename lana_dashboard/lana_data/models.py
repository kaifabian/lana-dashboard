from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from colorfield.fields import ColorField
import netfields


class Institution(models.Model):
	name = models.CharField(max_length=255, unique=True, verbose_name=_("Name"))
	code = models.CharField(max_length=8, unique=True, verbose_name=_("Code"))
	abuse_email = models.EmailField(blank=True, verbose_name=_("Abuse Email"))
	color = ColorField(default="#808080", verbose_name=_("Institution Color"))

	owners = models.ManyToManyField(User, related_name='institutions', verbose_name=_("Managers"))

	class Meta:
		ordering = ['code']
		verbose_name = ungettext_lazy("Institution", "Institutions", 1)
		verbose_name_plural = ungettext_lazy("Institution", "Institutions", 2)

	def __str__(self):
		return self.name

	def can_edit(self, user):
		return self.owners.filter(id=user.id).exists()


class AutonomousSystem(models.Model):
	as_number = models.BigIntegerField(unique=True, verbose_name=_("AS Number"))
	fqdn = models.CharField(max_length=255, verbose_name=_("FQDN"))
	comment = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Comment"))
	location_lat = models.FloatField(blank=True, null=True, verbose_name=_("Latitude"))
	location_lng = models.FloatField(blank=True, null=True, verbose_name=_("Longitude"))

	institution = models.ForeignKey(Institution, related_name='autonomous_systems', verbose_name=_("Institution"))

	class Meta:
		ordering = ['as_number']
		verbose_name = ungettext_lazy("Autonomous System", "Autonomous Systems", 1)
		verbose_name_plural = ungettext_lazy("Autonomous System", "Autonomous Systems", 2)

	def __str__(self):
		return "AS{}".format(self.as_number)

	def can_edit(self, user):
		return self.institution.can_edit(user)


class IPv4Subnet(models.Model):
	network = netfields.CidrAddressField(unique=True, verbose_name=_("Network"))
	dns_server = netfields.InetAddressField(blank=True, null=True, verbose_name=_("DNS Server"))
	comment = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Comment"))

	institution = models.ForeignKey(Institution, related_name='ipv4_subnets', verbose_name=_("Institution"))

	objects = netfields.NetManager()

	class Meta:
		ordering = ['network']
		verbose_name = ungettext_lazy("IPv4 Subnet", "IPv4 Subnets", 1)
		verbose_name_plural = ungettext_lazy("IPv4 Subnet", "IPv4 Subnets", 2)

	def __str__(self):
		return str(self.network)

	def can_edit(self, user):
		return self.institution.can_edit(user)


class TunnelEndpoint(models.Model):
	external_ipv4 = netfields.InetAddressField(blank=True, null=True, verbose_name=_("External IPv4 address"))
	internal_ipv4 = netfields.InetAddressField(blank=True, null=True, verbose_name=_("Internal IPv4 address"))
	port = models.IntegerField(blank=True, null=True, verbose_name=_("Port"), help_text=_('Defaults to remote AS number if ≤ 65535 (Fastd only).'))

	autonomous_system = models.ForeignKey(AutonomousSystem, related_name='tunnel_endpoints', verbose_name=_("Autonomous System"))

	public_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Public key"))

	objects = netfields.NetManager()

	def can_edit(self, user):
		return self.autonomous_system.can_edit(user)

	def is_config_complete(self, protocol):
		if protocol == Tunnel.PROTOCOL_FASTD:
			return bool(self.external_ipv4) and bool(self.internal_ipv4) and bool(self.port) and bool(self.public_key)
		return False


class Tunnel(models.Model):
	PROTOCOL_FASTD = 'fastd'
	PROTOCOL_OTHER = 'other'

	MODE_TUN = 'tun'
	MODE_TAP = 'tap'

	protocol = models.CharField(max_length=5, choices=(
		(PROTOCOL_FASTD, _("Fastd tunnel")),
		(PROTOCOL_OTHER, _("Other")),
	), verbose_name=_("Protocol"))
	mode = models.CharField(max_length=3, choices=(
		(MODE_TUN, 'tun'),
		(MODE_TAP, 'tap'),
	), verbose_name=_("Mode"))
	comment = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Comment"))

	encryption_method = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Encryption method"))
	mtu = models.IntegerField(blank=True, null=True, verbose_name=_("MTU"))

	endpoint1 = models.OneToOneField(TunnelEndpoint, on_delete=models.CASCADE, related_name='tunnel1', verbose_name=_("Endpoint 1"))
	endpoint2 = models.OneToOneField(TunnelEndpoint, on_delete=models.CASCADE, related_name='tunnel2', verbose_name=_("Endpoint 2"))

	class Meta:
		ordering = ['endpoint1__autonomous_system__as_number', 'endpoint2__autonomous_system__as_number']

	def __str__(self):
		return "{}-{}".format(self.endpoint1.autonomous_system, self.endpoint2.autonomous_system)

	def can_edit(self, user):
		return self.endpoint1.can_edit(user) or self.endpoint2.can_edit(user)

	def supports_config_generation(self):
		return self.protocol in [self.PROTOCOL_FASTD]

	def is_config_complete(self):
		if self.protocol == Tunnel.PROTOCOL_FASTD:
			return bool(self.encryption_method) and bool(self.mtu) and self.endpoint1.is_config_complete(self.protocol) and self.endpoint2.is_config_complete(self.protocol)
		return False

	def get_config_generation_url(self, endpoint_number):
		if self.protocol == Tunnel.PROTOCOL_FASTD:
			return reverse('lana_generator:generate-fastd', kwargs={
				'as_number1': self.endpoint1.autonomous_system.as_number,
				'as_number2': self.endpoint2.autonomous_system.as_number,
				'endpoint_number': endpoint_number,
			})
		return None
