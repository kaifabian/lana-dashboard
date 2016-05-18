from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.vary import vary_on_headers

from lana_dashboard.lana_data.forms import AutonomousSystemForm
from lana_dashboard.lana_data.models import AutonomousSystem, Institution, Tunnel
from lana_dashboard.lana_data.utils import geojson_from_autonomous_systems


@login_required
@vary_on_headers('Content-Type')
def list_autonomous_systems(request):
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return list_autonomous_systems_geojson(request)
	else:
		return list_autonomous_systems_web(request)


def list_autonomous_systems_geojson(request):
	autonomous_systems = AutonomousSystem.objects.all()
	return JsonResponse(geojson_from_autonomous_systems(autonomous_systems))


def list_autonomous_systems_web(request):
	autonomous_systems = AutonomousSystem.objects.all()
	can_create = Institution.objects.filter(owners=request.user.id).exists()

	return render(request, 'autonomous_systems_list.html', {
		'header_active': 'autonomous_systems',
		'autonomous_systems': autonomous_systems,
		'can_create': can_create,
	})


@login_required
def edit_autonomous_system(request, as_number=None):
	if as_number:
		mode = 'edit'
		autonomous_system = get_object_or_404(AutonomousSystem, as_number=as_number)
		if not autonomous_system.can_edit(request.user):
			raise PermissionDenied
	else:
		mode = 'create'
		autonomous_system = AutonomousSystem()
		institution_code = request.GET.get('institution', None)
		if institution_code:
			autonomous_system.institution = Institution.objects.get(code=institution_code)

	# model.is_valid() modifies model. :(
	original = {
		'as_number': autonomous_system.as_number,
	}

	if request.method == 'POST':
		form = AutonomousSystemForm(instance=autonomous_system, data=request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('lana_data:autonomous_system-details', kwargs={'as_number': autonomous_system.as_number}))
	else:
		form = AutonomousSystemForm(instance=autonomous_system)

	form.fields['institution'].queryset = Institution.objects.filter(owners=request.user.id)

	form.helper = FormHelper()
	form.helper.form_class = 'form-horizontal'
	form.helper.label_class = 'col-xs-4 col-md-3 col-lg-2'
	form.helper.field_class = 'col-xs-8 col-md-6 col-lg-5 col-xl-4'
	form.helper.html5_required = True
	if mode == 'create':
		form.helper.add_input(Submit("submit", "Create"))
	else:
		form.helper.add_input(Submit("submit", "Save"))

	return render(request, 'autonomous_systems_edit.html', {
		'header_active': 'autonomous_systems',
		'mode': mode,
		'original': original,
		'form': form,
	})


@login_required
@vary_on_headers('Content-Type')
def show_autonomous_system(request, as_number=None):
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return show_autonomous_system_geojson(request, as_number=as_number)
	else:
		return show_autonomous_system_web(request, as_number=as_number)


def show_autonomous_system_geojson(request, as_number=None):
	autonomous_system = get_object_or_404(AutonomousSystem, as_number=as_number)
	return JsonResponse(geojson_from_autonomous_systems([autonomous_system]))


def show_autonomous_system_web(request, as_number=None):
	autonomous_system = get_object_or_404(AutonomousSystem, as_number=as_number)
	tunnels = Tunnel.objects.all().filter(Q(endpoint1__autonomous_system__as_number=as_number) | Q(endpoint2__autonomous_system__as_number=as_number))

	for tunnel in tunnels:
		if tunnel.endpoint1.autonomous_system.as_number == int(as_number):
			tunnel.peer_endpoint = tunnel.endpoint2
		else:
			tunnel.peer_endpoint = tunnel.endpoint1

	return render(request, 'autonomous_systems_details.html', {
		'header_active': 'autonomous_systems',
		'autonomous_system': autonomous_system,
		'tunnels': tunnels,
		'can_edit': autonomous_system.can_edit(request.user),
	})
