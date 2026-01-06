from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import AccessLog
from .serializers import AccessLogSerializer


class AccessLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet that supports full CRUD operations for AccessLog.
    
    Supported endpoints:
    - POST /api/logs/ - Create a new log
    - GET /api/logs/ - Retrieve all logs
    - GET /api/logs/<id>/ - Retrieve a specific log
    - PUT /api/logs/<id>/ - Update a log
    - DELETE /api/logs/<id>/ - Delete a log
    """
    
    queryset = AccessLog.objects.all()
    serializer_class = AccessLogSerializer
    
    # Filtering and search support
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['card_id', 'door_name', 'access_granted']
    search_fields = ['card_id', 'door_name']
    ordering_fields = ['timestamp', 'created_at']
    ordering = ['-timestamp']
    
    def create(self, request, *args, **kwargs):
        """
        Create a new AccessLog entry.
        Response status: 201 Created
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete an AccessLog entry.
        Response status: 204 No Content
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def by_card(self, request):
        """
        Retrieve all logs for a specific card_id.
        Usage: GET /api/logs/by_card/?card_id=C1001
        """
        card_id = request.query_params.get('card_id')
        if not card_id:
            return Response(
                {'error': 'Please provide the card_id parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = AccessLog.objects.filter(card_id=card_id)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_door(self, request):
        """
        Retrieve all logs for a specific door_name.
        Usage: GET /api/logs/by_door/?door_name=Main%20Entrance
        """
        door_name = request.query_params.get('door_name')
        if not door_name:
            return Response(
                {'error': 'Please provide the door_name parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = AccessLog.objects.filter(door_name=door_name)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def denied_access(self, request):
        """
        Retrieve only denied access entries.
        Usage: GET /api/logs/denied_access/
        """
        logs = AccessLog.objects.filter(access_granted=False)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Retrieve overall statistics.
        Usage: GET /api/logs/stats/
        """
        total_logs = AccessLog.objects.count()
        granted_count = AccessLog.objects.filter(access_granted=True).count()
        denied_count = AccessLog.objects.filter(access_granted=False).count()
        unique_cards = AccessLog.objects.values('card_id').distinct().count()
        unique_doors = AccessLog.objects.values('door_name').distinct().count()
        
        return Response({
            'total_logs': total_logs,
            'granted_access': granted_count,
            'denied_access': denied_count,
            'unique_cards': unique_cards,
            'unique_doors': unique_doors,
        })
