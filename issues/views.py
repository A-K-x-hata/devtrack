from django.shortcuts import render

# Create your views here.
import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from issues.models import Reporter, Issue, CriticalIssue, LowPriorityIssue 

REPORTERS_FILE = 'reporters.json'
ISSUES_FILE = 'issues.json'

def read_json(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def write_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

@csrf_exempt
def reporters_view(request):
    if request.method == 'GET':
        reporter_id = request.GET.get('id')
        reporters = read_json(REPORTERS_FILE)
        
        if reporter_id is not None:
            for r in reporters:
                if r['id'] == int(reporter_id):
                    return JsonResponse(r, status=200)
            return JsonResponse({'error': 'Reporter not found'}, status=404)
            
        return JsonResponse(reporters, safe=False, status=200)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            reporter = Reporter(
                id=data.get('id'),
                name=data.get('name'),
                email=data.get('email'),
                team=data.get('team')
            )
            reporter.validate()
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Invalid request body'}, status=400)

        reporters = read_json(REPORTERS_FILE)
        reporters.append(reporter.to_dict())
        write_json(REPORTERS_FILE, reporters)

        return JsonResponse(reporter.to_dict(), status=201)

@csrf_exempt
def issues_view(request):
    if request.method == 'GET':
        issue_id = request.GET.get('id')
        status = request.GET.get('status')
        issues = read_json(ISSUES_FILE)

        if issue_id is not None:
            for issue in issues:
                if issue['id'] == int(issue_id):
                    return JsonResponse(issue, status=200)
            return JsonResponse({'error': 'Issue not found'}, status=404)

        if status is not None:
            filtered_issues = [issue for issue in issues if issue['status'] == status]
            return JsonResponse(filtered_issues, safe=False, status=200)

        return JsonResponse(issues, safe=False, status=200)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            priority = data.get('priority')

            if priority == 'critical':
                issue = CriticalIssue(
                    id=data.get('id'),
                    title=data.get('title'),
                    description=data.get('description'),
                    status=data.get('status'),
                    priority=priority,
                    reporter_id=data.get('reporter_id')
                )
            elif priority == 'low':
                issue = LowPriorityIssue(
                    id=data.get('id'),
                    title=data.get('title'),
                    description=data.get('description'),
                    status=data.get('status'),
                    priority=priority,
                    reporter_id=data.get('reporter_id')
                )
            else:
                issue = Issue(
                    id=data.get('id'),
                    title=data.get('title'),
                    description=data.get('description'),
                    status=data.get('status'),
                    priority=priority,
                    reporter_id=data.get('reporter_id')
                )

            issue.validate()
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Invalid request body'}, status=400)

        response_data = issue.to_dict()
        response_data['message'] = issue.describe()

        issues = read_json(ISSUES_FILE)
        issues.append(response_data)
        write_json(ISSUES_FILE, issues)

        return JsonResponse(response_data, status=201)