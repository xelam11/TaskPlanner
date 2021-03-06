from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .filters import BoardFilter
from .models import (Board, Favorite, ParticipantInBoard)
from .permissions import (IsAuthor, IsParticipant, IsStaff,
                          IsAuthorOrParticipantOrAdminListParticipantsAndTags,
                          IsAuthorOrModeratorOrAdminDelParticipantsPutTags)
from .serializers import (BoardListOrCreateSerializer, BoardSerializer,
                          ParticipantInBoardSerializer,
                          SwitchModeratorSerializer,
                          SearchBoardSerializer, SearchCardSerializer)
from .tag_serializer import TagSerializer
from cards.models import Card


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

        if self.action in ('retrieve', 'favorite', 'leave'):
            return [(IsAuthor | IsParticipant | IsStaff)()]

        if self.action in ('update', 'partial_update', 'destroy',
                           'switch_moderator'):
            return [(IsAuthor | IsStaff)()]

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
                    'message': '???? ?????? ???????????????? ???????????? ?????????? ?? ??????????????????!'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            count, _ = Favorite.objects.filter(user=user, board=board).delete()

            if count == 0:
                return Response({
                    'status': 'error',
                    'message': '???????????? ?????????? ?????? ?? ???????????? ??????????????????!'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def switch_moderator(self, request, **kwargs):
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)

        data = request.data
        data['board_id'] = kwargs.get('pk')
        serializer = SwitchModeratorSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        user_id = request.data['id']
        participant_in_board = get_object_or_404(ParticipantInBoard,
                                                 board=board,
                                                 participant__=user_id,
                                                 )

        if participant_in_board.is_moderator:
            participant_in_board.is_moderator = False
            participant_in_board.save()

            return Response(
                {'status': 'success',
                 'message': '???????????? ???????????????????????? ???????????? ???? ??????????????????!'},
                status=status.HTTP_200_OK)

        participant_in_board.is_moderator = True
        participant_in_board.save()

        return Response({'status': 'success',
                         'message': '???????????? ???????????????????????? ???????????? ??????????????????!'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def leave(self, request, **kwargs):
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)

        if request.user == board.author:
            return Response({
                'status': 'error',
                'message': '?????????? ?????????? ???? ?????????? ???????????????? ??????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        board.participants.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ParticipantInBoardViewSet(viewsets.GenericViewSet,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin):
    serializer_class = ParticipantInBoardSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_moderator']

    def get_queryset(self):
        board = get_object_or_404(Board, id=self.kwargs.get('board_id'))

        return ParticipantInBoard.objects.filter(board=board)

    def get_permissions(self):

        if self.action == 'list':
            return [IsAuthorOrParticipantOrAdminListParticipantsAndTags()]

        if self.action == 'retrieve':
            return [(IsAuthor | IsParticipant | IsStaff)()]

        if self.action == 'destroy':
            return [IsAuthorOrModeratorOrAdminDelParticipantsPutTags()]

    def destroy(self, request, *args, **kwargs):
        board = get_object_or_404(Board, id=kwargs.get('board_id'))
        user_id = kwargs.get('pk')
        participant_in_board = get_object_or_404(ParticipantInBoard,
                                                 board=board,
                                                 participant__id=user_id,
                                                 )

        if participant_in_board.participant == board.author:
            return Response({
                'status': 'error',
                'message': '???????????? ?????????? ???????????? ?????????????????? ???? ????????????????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        if participant_in_board.is_moderator and request.user != board.author:
            return Response({
                'status': 'error',
                'message': '?????????????????? ???????????????????? ?????????? ???????????? ?????????? ??????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        board.participants.remove(user_id)

        for list_ in board.lists.all():
            for card in list_.cards.all():
                card.participants.remove(user_id)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TagInBoardViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin):
    serializer_class = TagSerializer

    def get_queryset(self):
        board = get_object_or_404(Board, id=self.kwargs.get('board_id'))

        return board.tags.all()

    def get_permissions(self):

        if self.action == 'list':
            return [IsAuthorOrParticipantOrAdminListParticipantsAndTags()]

        if self.action == 'retrieve':
            return [(IsAuthor | IsParticipant | IsStaff)()]

        if self.action in ('update', 'partial_update',):
            return [IsAuthorOrModeratorOrAdminDelParticipantsPutTags()]


class SearchAPIView(APIView):

    def get(self, request):
        name = request.GET.get('name', None)
        boards = Board.objects.filter(participants__id=self.request.user.id)
        cards = Card.objects.filter(
            list__board__participants__id=self.request.user.id)

        if name:
            boards = boards.filter(name__icontains=name)
            cards = cards.filter(name__icontains=name)

            return JsonResponse({
                'boards': SearchBoardSerializer(instance=boards,
                                                many=True).data,
                'cards': SearchCardSerializer(instance=cards,
                                              many=True).data
            })

        return JsonResponse({'boards': [], 'cards': []})
