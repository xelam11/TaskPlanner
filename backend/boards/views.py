from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import CustomUser

from .filters import BoardFilter, ParticipantsFilter
from .models import (Board, Favorite, ParticipantInBoard, Tag)
from .permissions import IsAuthor, IsParticipant, IsStaff, IsModerator
from .serializers import (BoardListOrCreateSerializer, BoardSerializer,
                          ParticipantInBoardSerializer,
                          SwitchModeratorSerializer,
                          DeleteParticipantSerializer)
                          # SearchBoardSerializer, SearchCardSerializer)
from .tag_serializer import TagSerializer


class BoardViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, ]
    filter_class = BoardFilter

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Board.objects.all()

        return Board.objects.filter(participants__id=self.request.user.id)

    def get_serializer_class(self):

        if self.action in ('list', 'create'):
            return BoardListOrCreateSerializer

        if self.action in ('retrieve', 'update', 'partial_update', 'destroy'):
            return BoardSerializer

    def get_permissions(self):

        if self.action in ('list', 'create'):
            return [IsAuthenticated()]

        if self.action in ('retrieve', 'favorite', 'leave', 'participants'):
            return [(IsAuthor | IsParticipant | IsStaff)()]

        if self.action in ('update', 'partial_update', 'destroy',
                           'switch_moderator'):
            return [(IsAuthor | IsStaff)()]

        if self.action in ('delete_participant', 'edit_tag'):
            return [(IsAuthor | IsModerator | IsStaff)()]

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, **kwargs):
        user = request.user
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)

        if request.method == 'POST':
            _, is_created = Favorite.objects.get_or_create(user=user,
                                                           board=board)

            if not is_created:
                return Response({
                    'status': 'error',
                    'message': 'Вы уже добавили данную доску в избранное!'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            count, _ = Favorite.objects.filter(
                user=user,
                board=board).delete()

            if count == 0:
                return Response({
                    'status': 'error',
                    'message': 'Данной доски нет в списке избранных!'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, filter_class=ParticipantsFilter)
    def participants(self, request, **kwargs):
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)

        qs_participants = self.filter_queryset(
            ParticipantInBoard.objects.filter(board=board))
        page = self.paginate_queryset(qs_participants)

        if page is not None:
            serializer = ParticipantInBoardSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ParticipantInBoardSerializer(qs_participants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def edit_tag(self, request, **kwargs):
        serializer = TagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)
        tag = get_object_or_404(Tag, id=request.data['id'])
        name = request.data['name']

        tag.name = name
        tag.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def switch_moderator(self, request, **kwargs):
        serializer = SwitchModeratorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.data['id']
        participant = get_object_or_404(CustomUser, id=user_id)
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)
        participant_in_board = get_object_or_404(ParticipantInBoard,
                                                 board=board,
                                                 participant=participant,
                                                 )

        if request.user == participant:
            return Response({
                'status': 'error',
                'message': 'Автор доски всегда должен быть модератором!'},
                status=status.HTTP_400_BAD_REQUEST)

        if participant_in_board.is_moderator:
            participant_in_board.is_moderator = False
            participant_in_board.save()

            return Response(
                {'status': 'success',
                 'message': 'Данный пользователь больше не модератор!'},
                status=status.HTTP_200_OK)

        participant_in_board.is_moderator = True
        participant_in_board.save()

        return Response({'status': 'success',
                         'message': 'Данный пользователь теперь модератор!'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def delete_participant(self, request, **kwargs):
        serializer = DeleteParticipantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.data['id']
        participant = get_object_or_404(CustomUser, id=user_id)
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)
        participant_in_board = get_object_or_404(ParticipantInBoard,
                                                 board=board,
                                                 participant=participant,
                                                 )
        if participant == board.author:
            return Response({
                'status': 'error',
                'message': 'Автора доски нельзя исключить из участников!'},
                status=status.HTTP_400_BAD_REQUEST)

        if request.user == board.author:
            board.participants.remove(participant)
            return Response(status=status.HTTP_204_NO_CONTENT)

        if participant_in_board.is_moderator:
            return Response({
                'status': 'error',
                'message': 'Исключить модератора может только автор доски!'},
                status=status.HTTP_400_BAD_REQUEST)

        board.participants.remove(participant)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def leave(self, request, **kwargs):
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)

        if request.user == board.author:
            return Response({
                'status': 'error',
                'message': 'Автор доски не может покинуть доску!'},
                status=status.HTTP_400_BAD_REQUEST)

        board.participants.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


# class SearchAPIView(APIView):
#
#     def get(self, request):
#         name = request.GET.get('name', None)
#         boards = Board.objects.filter(participants__id=self.request.user.id)
#         cards = Card.objects.filter(
#             list__board__participants__id=self.request.user.id)
#
#         if name:
#             boards = boards.filter(name__icontains=name)
#             cards = cards.filter(name__icontains=name)
#
#             return JsonResponse({
#                 'boards': SearchBoardSerializer(instance=boards,
#                                                 many=True).data,
#                 'cards': SearchCardSerializer(instance=cards,
#                                               many=True).data
#             })
#
#         return JsonResponse({'boards': [], 'cards': []})
