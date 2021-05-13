from typing import Any, Tuple, Dict, Optional, OrderedDict, Union
from djangochannelsrestframework.observer.model_observer import Action
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from djangochannelsrestframework.mixins import ListModelMixin
from djangochannelsrestframework.decorators import action
from rest_framework import status as rest_status
class PaginatedModelListMixin(ListModelMixin):

    pagination_class = None

    @action()
    def list(self, **kwargs):
        queryset = self.filter_queryset(self.get_queryset(**kwargs), **kwargs)
        page = self.paginate_queryset(queryset, **kwargs)
        if page is not None:
            serializer = self.get_serializer(
                instance=page, many=True, action_kwargs=kwargs
            )
            return self.get_paginated_response(serializer.data), status.HTTP_200_OK

        serializer = self.get_serializer(
            instance=queryset, many=True, action_kwargs=kwargs
        )
        return serializer.data, status.HTTP_200_OK

    @property
    def paginator(self) -> Optional[any]:
        """Gets the paginator class
        Returns:
            Pagination class. Optional.
        """
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(
        self, queryset, **kwargs: Dict
    ) -> Optional[Any]:
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(
            queryset, self.scope, view=self, **kwargs
        )

    def get_paginated_response(
        self, data: Union[ReturnDict, ReturnList]
    ) -> OrderedDict:
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class StreamedPaginatedListMixin(PaginatedModelListMixin):
    @action()
    async def list(self, action, request_id, **kwargs):
        data, status = await super().list(
            action=action, request_id=request_id, **kwargs
        )

        await self.reply(action=action, data=data, status=status, request_id=request_id)

        count = data.get("count", 0)
        limit = data.get("limit", 0)
        offset = data.get("offset", 0)

        if offset < (count - limit):
            kwargs["offset"] = limit + offset

            await self.list(action=action, request_id=request_id, **kwargs)
        # if offset >= (count - limit):
        #     await self.reply(action=action, data=dict(end=True), status=rest_status.HTTP_204_NO_CONTENT, request_id=request_id)