"""
CSC148, Winter 2023
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import time
import datetime
from call import Call
from customer import Customer


class Filter:
    """ A class for filtering customer data on some criterion. A filter is
    applied to a set of calls.

    This is an abstract class. Only subclasses should be instantiated.
    """
    def __init__(self) -> None:
        pass

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all calls from <data>, which match the filter
        specified in <filter_string>.

        The <filter_string> is provided by the user through the visual prompt,
        after selecting this filter.
        The <customers> is a list of all customers from the input dataset.

         If the filter has
        no effect or the <filter_string> is invalid then return the same calls
        from the <data> input.

        Note that the order of the output matters, and the output of a filter
        should have calls ordered in the same manner as they were given, except
        for calls which have been removed.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        - all calls included in <data> are valid calls from the input dataset
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        raise NotImplementedError


class ResetFilter(Filter):
    """
    A class for resetting all previously applied filters, if any.
    """
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Reset all of the applied filters. Return a List containing all the
        calls corresponding to <customers>.
        The <data> and <filter_string> arguments for this type of filter are
        ignored.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        """
        filtered_calls = []
        for c in customers:
            customer_history = c.get_history()
            # only take outgoing calls, we don't want to include calls twice
            filtered_calls.extend(customer_history[0])
        return filtered_calls

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Reset all of the filters applied so far, if any"


class CustomerFilter(Filter):
    """
    A class for selecting only the calls from a given customer.
    """
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data> made or
        received by the customer with the id specified in <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains a valid
        customer ID.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """
        if filter_string.isdigit():
            total_custs = 0
            for cust in customers:
                if cust.get_id() == int(filter_string):
                    total_custs += 1
            if total_custs == 1:
                return _customer_calls(data, customers, filter_string)
            else:
                return data
        else:
            return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter events based on customer ID"


class DurationFilter(Filter):
    """
    A class for selecting only the calls lasting either over or under a
    specified duration.
    """
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data> with a duration
        of under or over the time indicated in the <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains the following
        input format: either "Lxxx" or "Gxxx", indicating to filter calls less
        than xxx or greater than xxx seconds, respectively.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """
        if 2 <= len(filter_string) <= 4:
            first = filter_string[0].upper()
            end = filter_string[1:]
            if (first in ('L', 'G')) and end.isdigit():
                if 0 <= int(end) <= 999:
                    calls = []
                    if first == 'G':
                        for call in data:
                            if call.duration > int(end) and call not in calls:
                                calls.append(call)
                    else:
                        for call in data:
                            if call.duration < int(end) and call not in calls:
                                calls.append(call)
                    return calls
                else:
                    return data
            else:
                return data
        else:
            return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls based on duration; " \
               "L### returns calls less than specified length, G### for greater"


class LocationFilter(Filter):
    """
    A class for selecting only the calls that took place within a specific area
    """
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data>, which took
        place within a location specified by the <filter_string>
        (at least the source or the destination of the event was
        in the range of coordinates from the <filter_string>).

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains four valid
        coordinates within the map boundaries.
        These coordinates represent the location of the lower left corner
        and the upper right corner of the search location rectangle,
        as 2 pairs of longitude/latitude coordinates, each separated by
        a comma and a space:
          lowerLong, lowerLat, upperLong, upperLat
        Calls that fall exactly on the boundary of this rectangle are
        considered a match as well.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """
        if _check_validity(filter_string):
            in_range = []
            loc = filter_string.split(',')
            l_lo = float(loc[0])
            l_lat = float(loc[1])
            u_lo = float(loc[2])
            u_lat = float(loc[3])
            for call in data:
                cs0 = call.src_loc[0]
                cs1 = call.src_loc[1]
                cd0 = call.dst_loc[0]
                cd1 = call.dst_loc[1]
                if ((l_lo <= cs0 <= u_lo) and (l_lat <= cs1 <= u_lat)) or \
                        ((l_lo <= cd0 <= u_lo) and (l_lat <= cd1 <= u_lat)):
                    if call not in in_range:
                        in_range.append(call)
            return in_range
        return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls made or received in a given rectangular area. " \
               "Format: \"lowerLong, lowerLat, " \
               "upperLong, upperLat\" (e.g., -79.6, 43.6, -79.3, 43.7)"


def _check_validity(s: str) -> bool:
    lower_lo = -79.697878
    lower_lat = 43.576959
    upper_lo = -79.196382
    upper_lat = 43.799568
    if ',' in s:
        lst = []
        s_lst = s.split(',')
        if len(s_lst) == 4:
            for loc in s_lst:
                try:
                    lst.append(float(loc))
                except ValueError:
                    return False
            if lst[0] <= lst[2] and lst[1] <= lst[3]:
                if (lower_lo <= lst[0]) and (lower_lat <= lst[1])  \
                        and (lst[2] <= upper_lo) and (lst[3] <= upper_lat):
                    return True
        return False
    return False


def _customer_calls(data: list[Call],
                    customers: list[Customer], s: str) -> list[Call]:
    uni_calls = []
    for cust in customers:
        if cust.get_id() == int(s):
            for call in data:
                history = cust.get_history()
                if call in history[0] or call in history[1] and \
                    call not in uni_calls:
                    uni_calls.append(call)
    return uni_calls


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'time', 'datetime', 'call', 'customer'
        ],
        'max-nested-blocks': 4,
        'allowed-io': ['apply', '__str__'],
        'disable': ['W0611', 'W0703'],
        'generated-members': 'pygame.*'
    })
